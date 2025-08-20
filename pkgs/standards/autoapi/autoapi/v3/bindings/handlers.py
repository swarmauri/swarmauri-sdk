# autoapi/v3/bindings/handlers.py
from __future__ import annotations

import inspect
import logging
import uuid
from types import SimpleNamespace
from typing import Any, Callable, Mapping, Optional, Sequence, Tuple

from ..opspec import OpSpec
from ..opspec.types import StepFn
from .. import core as _core

# Optional SQLAlchemy type import — only used for safe checks (no hard dependency)
try:  # pragma: no cover
    from sqlalchemy.inspection import inspect as _sa_inspect  # type: ignore
except Exception:  # pragma: no cover
    _sa_inspect = None  # type: ignore
try:  # pragma: no cover
    from sqlalchemy.sql import ClauseElement as SAClause  # type: ignore
except Exception:  # pragma: no cover
    SAClause = None  # type: ignore

logger = logging.getLogger(__name__)

_Key = Tuple[str, str]  # (alias, target)

# ───────────────────────────────────────────────────────────────────────────────
# Helpers: model.hooks / model.handlers alias namespaces
# ───────────────────────────────────────────────────────────────────────────────


def _ensure_alias_hooks_ns(model: type, alias: str) -> SimpleNamespace:
    hooks_root = getattr(model, "hooks", None)
    if hooks_root is None:
        hooks_root = SimpleNamespace()
        setattr(model, "hooks", hooks_root)

    ns = getattr(hooks_root, alias, None)
    if ns is None:
        ns = SimpleNamespace()
        setattr(hooks_root, alias, ns)

    # Ensure per-phase lists exist for executor consumption
    if not hasattr(ns, "HANDLER"):
        setattr(ns, "HANDLER", [])
    return ns


def _ensure_alias_handlers_ns(model: type, alias: str) -> SimpleNamespace:
    handlers_root = getattr(model, "handlers", None)
    if handlers_root is None:
        handlers_root = SimpleNamespace()
        setattr(model, "handlers", handlers_root)

    ns = getattr(handlers_root, alias, None)
    if ns is None:
        ns = SimpleNamespace()
        setattr(handlers_root, alias, ns)
    return ns


def _append_handler_step(model: type, alias: str, step: StepFn) -> None:
    ns = _ensure_alias_hooks_ns(model, alias)
    chain: list[StepFn] = getattr(ns, "HANDLER")
    chain.append(step)


# ───────────────────────────────────────────────────────────────────────────────
# Payload/ctx helpers
# ───────────────────────────────────────────────────────────────────────────────


def _ctx_get(ctx: Mapping[str, Any], key: str, default: Any = None) -> Any:
    try:
        return ctx[key]
    except Exception:
        return getattr(ctx, key, default)


def _ctx_payload(ctx: Mapping[str, Any]) -> Mapping[str, Any]:
    v = _ctx_get(ctx, "payload", None)
    # Never let non-mapping (incl. SQLA ClauseElement) flow as payload
    return v if isinstance(v, Mapping) else {}


def _ctx_db(ctx: Mapping[str, Any]) -> Any:
    return _ctx_get(ctx, "db")


def _ctx_request(ctx: Mapping[str, Any]) -> Any:
    return _ctx_get(ctx, "request")


def _ctx_path_params(ctx: Mapping[str, Any]) -> Mapping[str, Any]:
    v = _ctx_get(ctx, "path_params", None)
    return v if isinstance(v, Mapping) else {}


# ───────────────────────────────────────────────────────────────────────────────
# PK discovery & identifier coercion
# ───────────────────────────────────────────────────────────────────────────────


def _pk_name(model: type) -> str:
    """
    Best-effort primary-key column name:
      • Prefer mapper.primary_key (most reliable),
      • Fallback to __table__.primary_key.columns,
      • Else 'id'.
    """
    # Prefer mapper inspection when available
    if _sa_inspect is not None:
        try:
            mapper = _sa_inspect(model)
            pk_cols = list(getattr(mapper, "primary_key", []) or [])
            if len(pk_cols) == 1:
                col = pk_cols[0]
                name = getattr(col, "key", None) or getattr(col, "name", None)
                if isinstance(name, str) and name:
                    return name
        except Exception:
            pass

    # Fallback to __table__
    table = getattr(model, "__table__", None)
    if table is not None:
        try:
            pk = getattr(table, "primary_key", None)
            cols_iter = getattr(pk, "columns", None)
            cols = [c for c in cols_iter] if cols_iter is not None else []
            if len(cols) == 1:
                col = cols[0]
                name = getattr(col, "key", None) or getattr(col, "name", None)
                if isinstance(name, str) and name:
                    return name
        except Exception:
            pass

    return "id"


def _pk_type_info(model: type) -> tuple[Optional[type], Optional[Any]]:
    """
    Return (python_type, sqlatype_instance) for the PK column if discoverable.
    """
    col = None
    if _sa_inspect is not None:
        try:
            mapper = _sa_inspect(model)
            pk_cols = list(getattr(mapper, "primary_key", []) or [])
            if len(pk_cols) == 1:
                col = pk_cols[0]
        except Exception:
            col = None

    if col is None:
        table = getattr(model, "__table__", None)
        if table is not None:
            try:
                pk = getattr(table, "primary_key", None)
                cols_iter = getattr(pk, "columns", None)
                cols = [c for c in cols_iter] if cols_iter is not None else []
                if len(cols) == 1:
                    col = cols[0]
            except Exception:
                col = None

    if col is None:
        return (None, None)

    try:
        coltype = getattr(col, "type", None)
    except Exception:
        coltype = None

    py_t = None
    try:
        py_t = getattr(coltype, "python_type", None)
    except Exception:
        py_t = None

    return (py_t, coltype)


def _looks_like_uuid_string(s: str) -> bool:
    if not isinstance(s, str):
        return False
    try:
        uuid.UUID(s)
        return True
    except Exception:
        return False


def _is_uuid_type(py_t: Optional[type], sa_type: Optional[Any]) -> bool:
    if py_t is uuid.UUID:
        return True
    # Heuristics when python_type isn't available
    try:
        if getattr(sa_type, "as_uuid", False):
            return True
    except Exception:
        pass
    try:
        tname = type(sa_type).__name__.lower() if sa_type is not None else ""
        if "uuid" in tname:
            return True
    except Exception:
        pass
    return False


def _coerce_ident_to_pk_type(model: type, value: Any) -> Any:
    """
    Coerce incoming identifier (often a string from path params) to the
    model PK's expected Python type (uuid.UUID, int, etc.). Safe no-op when
    type is unknown or value already matches.
    """
    py_t, sa_t = _pk_type_info(model)

    # ClauseElements are never identifiers here; caller already filters them.
    if SAClause is not None and isinstance(value, SAClause):  # pragma: no cover
        return value

    # UUID coercion
    if _is_uuid_type(py_t, sa_t):
        if isinstance(value, uuid.UUID):
            return value
        if isinstance(value, str):
            # Allow both dashed and hex-only forms
            return uuid.UUID(value)
        # Some frameworks pass bytes for UUID (16-byte); accept that too
        if isinstance(value, (bytes, bytearray)) and len(value) == 16:
            return uuid.UUID(bytes=bytes(value))
        # Last resort: stringify then parse if it looks like a UUID
        if _looks_like_uuid_string(str(value)):
            return uuid.UUID(str(value))
        return value  # let DB/type system complain if truly incompatible

    # Integer coercion
    if py_t is int:
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            return int(value)
        # floats etc. → try int() best-effort
        try:
            return int(value)  # type: ignore[arg-type]
        except Exception:
            return value

    # No known target type → leave as is
    return value


def _is_clause(x: Any) -> bool:
    return SAClause is not None and isinstance(x, SAClause)  # type: ignore[truthy-bool]


def _resolve_ident(model: type, ctx: Mapping[str, Any]) -> Any:
    """
    Extract scalar primary-key identifier for read/update/replace/delete without
    ever truth-testing SQLAlchemy expressions.

    Recognized keys (order of precedence):
      1) path_params[<pk>]
      2) payload[<pk>]
      3) path_params['id']
      4) payload['id']
      5) path_params['item_id']        ← added
      6) payload['item_id']            ← added
      7) path_params[f'{pk}_id']       ← added
      8) payload[f'{pk}_id']           ← added
      9) payload['ident']
    """
    payload = _ctx_payload(ctx)
    path = _ctx_path_params(ctx)
    pk = _pk_name(model)

    specs: Mapping[str, Any] = getattr(model, "__autoapi_cols__", {}) or {}
    alias = None
    spec = specs.get(pk)
    if spec is not None:
        alias = getattr(getattr(spec, "io", None), "alias_in", None)

    candidates_keys = [
        (path, pk),
        (payload, pk),
        (path, "id"),
        (payload, "id"),
        (path, "item_id"),
        (payload, "item_id"),
    ]
    if pk != "id":
        candidates_keys.extend(
            [
                (path, f"{pk}_id"),
                (payload, f"{pk}_id"),
            ]
        )
    if isinstance(alias, str) and alias:
        candidates_keys.extend([(path, alias), (payload, alias)])
    candidates_keys.append((payload, "ident"))

    for source, key in candidates_keys:
        try:
            v = source.get(key)  # type: ignore[call-arg]
        except Exception:
            v = None
        if v is None:
            continue
        if _is_clause(v):
            # Not a scalar identifier; likely a SQL filter expression → ignore
            continue
        # Coerce to PK's expected Python type (e.g., uuid.UUID for UUID PKs)
        try:
            return _coerce_ident_to_pk_type(model, v)
        except Exception:
            # If coercion fails (e.g., invalid UUID string), surface a clear error
            raise TypeError(f"Invalid identifier for '{pk}': {v!r}")

    raise TypeError(f"Missing identifier '{pk}' in path or payload")


# ───────────────────────────────────────────────────────────────────────────────
# Core → StepFn adapters
# ───────────────────────────────────────────────────────────────────────────────


async def _call_list_core(
    fn: Callable[..., Any],
    model: type,
    payload: Mapping[str, Any],
    ctx: Mapping[str, Any],
):
    """
    Call `_core.list` robustly across v2/v3 shapes, but ALWAYS include `db`.

      v2: async def list(model, filters, db, *, skip=None, limit=None, request=None)
      v3: async def list(model, *, filters, db, skip=None, limit=None, request=None)

    We try only call patterns that include `db` to avoid
    "missing 1 required keyword-only argument: 'db'".
    """
    # Build filters dict and pull pagination out
    filters = dict(payload) if isinstance(payload, Mapping) else {}
    skip = filters.pop("skip", None)
    limit = filters.pop("limit", None)
    filters_arg = filters if filters else None

    db = _ctx_db(ctx)
    req = _ctx_request(ctx)

    candidates: list[tuple[tuple, dict]] = []

    def add_candidate(
        use_pos_filters: bool, use_pos_db: bool, with_req: bool, with_pag: bool
    ):
        args: tuple = ()
        kwargs: dict = {}
        if use_pos_filters:
            args += (filters_arg,)
        else:
            kwargs["filters"] = filters_arg
        if use_pos_db:
            args += (db,)
        else:
            kwargs["db"] = db
        if with_req and req is not None:
            kwargs["request"] = req
        if with_pag:
            if skip is not None:
                kwargs["skip"] = skip
            if limit is not None:
                kwargs["limit"] = limit
        candidates.append((args, kwargs))

    # Richest → minimal, always passing db
    add_candidate(False, False, True, True)
    add_candidate(True, False, True, True)
    add_candidate(True, True, True, True)

    add_candidate(False, False, False, True)
    add_candidate(True, False, False, True)
    add_candidate(True, True, False, True)

    add_candidate(False, False, True, False)
    add_candidate(True, False, True, False)
    add_candidate(True, True, True, False)

    add_candidate(False, False, False, False)
    add_candidate(True, False, False, False)
    add_candidate(True, True, False, False)

    last_err: Optional[BaseException] = None
    for args, kwargs in candidates:
        try:
            rv = fn(model, *args, **kwargs)
            if inspect.isawaitable(rv):
                return await rv
            return rv
        except TypeError as e:
            last_err = e
            continue
    if last_err:
        raise last_err
    raise RuntimeError("list() call resolution failed unexpectedly")


def _accepted_kw(handler: Callable[..., Any]) -> set[str]:
    try:
        sig = inspect.signature(handler)
    except Exception:
        return {"ctx"}  # safest default

    names: set[str] = set()
    for p in sig.parameters.values():
        if p.kind in (p.VAR_KEYWORD, p.VAR_POSITIONAL):
            # **kwargs or *args → we can pass everything
            return {"ctx", "db", "payload", "request", "model", "op", "spec", "alias"}
        names.add(p.name)
    return names


def _wrap_custom(model: type, sp: OpSpec, user_handler: Callable[..., Any]) -> StepFn:
    """
    Wrap a user-supplied handler so it can be executed as StepFn(ctx).
    We pass keyword args selectively (ctx, db, payload, request, model, op/spec/alias).
    """
    wanted = _accepted_kw(user_handler)

    async def step(ctx: Any) -> Any:
        db = _ctx_db(ctx)
        payload = _ctx_payload(ctx)
        request = _ctx_request(ctx)

        # Try to resolve a *bound* attribute from the class if available
        bound = getattr(model, getattr(user_handler, "__name__", ""), user_handler)

        kw = {}
        if "ctx" in wanted:
            kw["ctx"] = ctx
        if "db" in wanted:
            kw["db"] = db
        if "payload" in wanted:
            kw["payload"] = payload
        if "request" in wanted:
            kw["request"] = request
        if "model" in wanted:
            kw["model"] = model
        if "op" in wanted:
            kw["op"] = sp
        if "spec" in wanted:
            kw["spec"] = sp
        if "alias" in wanted:
            kw["alias"] = sp.alias

        rv = bound(**kw)  # type: ignore[misc]
        if inspect.isawaitable(rv):
            return await rv
        return rv

    step.__name__ = getattr(user_handler, "__name__", step.__name__)
    step.__qualname__ = getattr(user_handler, "__qualname__", step.__name__)
    step.__module__ = getattr(user_handler, "__module__", step.__module__)
    return step


def _wrap_core(model: type, target: str) -> StepFn:
    """
    Turn a canonical core function into a StepFn(ctx) → Any.
    """

    async def step(ctx: Any) -> Any:
        db = _ctx_db(ctx)
        payload = _ctx_payload(ctx)

        if target == "create":
            return await _core.create(model, payload, db=db)

        if target == "read":
            ident = _resolve_ident(model, ctx)
            return await _core.read(model, ident, db=db)

        if target == "update":
            ident = _resolve_ident(model, ctx)
            return await _core.update(model, ident, payload, db=db)

        if target == "replace":
            ident = _resolve_ident(model, ctx)
            return await _core.replace(model, ident, payload, db=db)

        if target == "delete":
            ident = _resolve_ident(model, ctx)
            return await _core.delete(model, ident, db=db)

        if target == "list":
            return await _call_list_core(_core.list, model, payload, ctx)

        if target == "clear":
            return await _call_list_core(_core.clear, model, payload, ctx)

        if target == "bulk_create":
            rows = payload.get("rows") if isinstance(payload, Mapping) else None
            if rows is None:
                rows = []
            return await _core.bulk_create(model, rows, db=db)

        if target == "bulk_update":
            rows = payload.get("rows") if isinstance(payload, Mapping) else None
            if rows is None:
                rows = []
            return await _core.bulk_update(model, rows, db=db)

        if target == "bulk_replace":
            rows = payload.get("rows") if isinstance(payload, Mapping) else None
            if rows is None:
                rows = []
            return await _core.bulk_replace(model, rows, db=db)

        if target == "bulk_upsert":
            rows = payload.get("rows") if isinstance(payload, Mapping) else None
            if rows is None:
                rows = []
            return await _core.bulk_upsert(model, rows, db=db)

        if target == "bulk_delete":
            ids = payload.get("ids") if isinstance(payload, Mapping) else None
            if ids is None:
                ids = []
            return await _core.bulk_delete(model, ids, db=db)

        # Unknown canonical target – return payload to avoid hard failure
        return payload

    fn = getattr(_core, target, None)
    step.__name__ = getattr(fn, "__name__", step.__name__)
    step.__qualname__ = getattr(fn, "__qualname__", step.__name__)
    step.__module__ = getattr(fn, "__module__", step.__module__)
    return step


# ───────────────────────────────────────────────────────────────────────────────
# Builder
# ───────────────────────────────────────────────────────────────────────────────


def _build_raw_step(model: type, sp: OpSpec) -> StepFn:
    if sp.target == "custom" and sp.handler is not None:
        return _wrap_custom(model, sp, sp.handler)  # user function
    # Canonical/default core
    return _wrap_core(model, sp.target)


def _attach_one(model: type, sp: OpSpec) -> None:
    alias = sp.alias
    handlers_ns = _ensure_alias_handlers_ns(model, alias)
    _ensure_alias_hooks_ns(model, alias)

    raw_step = _build_raw_step(model, sp)

    # Attach v2-compatible attributes on handlers ns
    setattr(handlers_ns, "raw", raw_step)
    # For now handler == raw; PRE/POST behavior is governed by executor phases
    setattr(handlers_ns, "handler", raw_step)

    # Insert the raw step into the HANDLER phase chain
    _append_handler_step(model, alias, raw_step)

    # Update spec for introspection/back-compat
    try:
        sp.core = raw_step
        sp.core_raw = raw_step
    except Exception:
        # OpSpec may be frozen; surface them via handlers namespace
        setattr(handlers_ns, "core", raw_step)
        setattr(handlers_ns, "core_raw", raw_step)

    logger.debug(
        "handlers: %s.%s → raw step attached & inserted into HANDLER",
        model.__name__,
        alias,
    )


# ───────────────────────────────────────────────────────────────────────────────
# Public API
# ───────────────────────────────────────────────────────────────────────────────


def build_and_attach(
    model: type, specs: Sequence[OpSpec], *, only_keys: Optional[Sequence[_Key]] = None
) -> None:
    """
    Build raw/core handlers for each OpSpec and insert them into the HANDLER phase chain.
    Also attaches:
        model.handlers.<alias>.raw
        model.handlers.<alias>.handler
        (and, if OpSpec is frozen, model.handlers.<alias>.core / core_raw)

    If `only_keys` is provided, limit work to those (alias,target) pairs.
    """
    wanted = set(only_keys or ())
    for sp in specs:
        key = (sp.alias, sp.target)
        if wanted and key not in wanted:
            continue
        _attach_one(model, sp)


__all__ = ["build_and_attach"]
