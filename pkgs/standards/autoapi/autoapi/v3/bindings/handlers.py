# autoapi/v3/bindings/handlers.py
from __future__ import annotations

import inspect
import logging
from types import SimpleNamespace
from typing import (
    Any,
    Callable,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)

from ..opspec import OpSpec
from ..opspec.types import StepFn
from .. import core as _core

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
# Payload extraction helpers
# ───────────────────────────────────────────────────────────────────────────────


def _ctx_get(ctx: Mapping[str, Any], key: str, default: Any = None) -> Any:
    try:
        return ctx[key]
    except Exception:
        return getattr(ctx, key, default)


def _ctx_payload(ctx: Mapping[str, Any]) -> Mapping[str, Any]:
    return _ctx_get(ctx, "payload", {}) or {}


def _ctx_db(ctx: Mapping[str, Any]) -> Any:
    return _ctx_get(ctx, "db")


def _ctx_request(ctx: Mapping[str, Any]) -> Any:
    return _ctx_get(ctx, "request")


def _ctx_path_params(ctx: Mapping[str, Any]) -> Mapping[str, Any]:
    return _ctx_get(ctx, "path_params", {}) or {}


def _pk_name(model: type) -> str:
    table = getattr(model, "__table__", None)
    if not table or not getattr(table, "primary_key", None):
        return "id"
    cols = list(table.primary_key.columns)  # type: ignore[attr-defined]
    if not cols:
        return "id"
    if len(cols) > 1:
        # For composite PKs, we fall back to "id" and expect adapters to supply ident explicitly.
        return "id"
    return getattr(cols[0], "name", "id")


def _resolve_ident(model: type, ctx: Mapping[str, Any]) -> Any:
    """
    Try to find an identifier in common places:
      • ctx.path_params[pk]
      • ctx.payload[pk]
      • ctx.payload["id"]
    """
    payload = _ctx_payload(ctx)
    path = _ctx_path_params(ctx)
    pk = _pk_name(model)
    if pk in path:
        return path[pk]
    if pk in payload:
        return payload[pk]
    if "id" in payload:
        return payload["id"]
    return None


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

    We try only call patterns that include `db` to avoid the
    "missing 1 required keyword-only argument: 'db'" error.
    """
    # Build filters dict and pull pagination out
    filters = dict(payload) if isinstance(payload, Mapping) else {}
    skip = filters.pop("skip", None)
    limit = filters.pop("limit", None)
    filters_arg = filters if filters else None

    db = _ctx_db(ctx)
    req = _ctx_request(ctx)

    # Candidate calls (ALL include db):
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

    # Try richer shapes first, then progressively simpler — but always include db.
    add_candidate(
        use_pos_filters=False, use_pos_db=False, with_req=True, with_pag=True
    )  # kw filters + kw db
    add_candidate(
        use_pos_filters=True, use_pos_db=False, with_req=True, with_pag=True
    )  # pos filters + kw db
    add_candidate(
        use_pos_filters=True, use_pos_db=True, with_req=True, with_pag=True
    )  # pos filters + pos db

    add_candidate(
        use_pos_filters=False, use_pos_db=False, with_req=False, with_pag=True
    )
    add_candidate(use_pos_filters=True, use_pos_db=False, with_req=False, with_pag=True)
    add_candidate(use_pos_filters=True, use_pos_db=True, with_req=False, with_pag=True)

    add_candidate(
        use_pos_filters=False, use_pos_db=False, with_req=True, with_pag=False
    )
    add_candidate(use_pos_filters=True, use_pos_db=False, with_req=True, with_pag=False)
    add_candidate(use_pos_filters=True, use_pos_db=True, with_req=True, with_pag=False)

    # Minimal (still with db)
    add_candidate(
        use_pos_filters=False, use_pos_db=False, with_req=False, with_pag=False
    )
    add_candidate(
        use_pos_filters=True, use_pos_db=False, with_req=False, with_pag=False
    )
    add_candidate(use_pos_filters=True, use_pos_db=True, with_req=False, with_pag=False)

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
            # No request body for clear; align with REST semantics.
            return await _core.clear(model, {}, db=db)

        if target == "bulk_create":
            rows = payload.get("rows") or []
            return await _core.bulk_create(model, rows, db=db)

        if target == "bulk_update":
            rows = payload.get("rows") or []
            return await _core.bulk_update(model, rows, db=db)

        if target == "bulk_replace":
            rows = payload.get("rows") or []
            return await _core.bulk_replace(model, rows, db=db)

        if target == "bulk_delete":
            ids = payload.get("ids") or []
            return await _core.bulk_delete(model, ids, db=db)

        # Unknown canonical target – return payload to avoid hard failure
        return payload

    fn = getattr(_core, target, None)
    step.__name__ = getattr(fn, "__name__", step.__name__)
    step.__qualname__ = getattr(fn, "__qualname__", step.__name__)
    step.__module__ = getattr(fn, "__module__", step.__module__)

    return step


def _accepted_kw(handler: Callable[..., Any]) -> set[str]:
    try:
        sig = inspect.signature(handler)
    except Exception:
        return {"ctx"}  # safest default

    names: set[str] = set()
    for p in sig.parameters.values():
        if p.kind in (p.VAR_KEYWORD, p.VAR_POSITIONAL):
            # **kwargs or *args → we can pass everything
            return {"ctx", "db", "payload", "request", "model", "op"}
        names.add(p.name)
    return names


def _wrap_custom(model: type, sp: OpSpec, user_handler: Callable[..., Any]) -> StepFn:
    """
    Wrap a user-supplied handler so it can be executed as StepFn(ctx).
    We pass keyword args selectively (ctx, db, payload, request, model, op).
    """
    wanted = _accepted_kw(user_handler)

    async def step(ctx: Any) -> Any:
        db = _ctx_db(ctx)
        payload = _ctx_payload(ctx)
        request = _ctx_request(ctx)

        # Try to resolve a *bound* attribute from the class if available (classmethod/staticmethod)
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

        rv = bound(**kw)  # type: ignore[misc]
        if inspect.isawaitable(rv):
            return await rv
        return rv

    step.__name__ = getattr(user_handler, "__name__", step.__name__)
    step.__qualname__ = getattr(user_handler, "__qualname__", step.__name__)
    step.__module__ = getattr(user_handler, "__module__", step.__module__)

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
        # OpSpec is frozen; ignore updating in-place (collector returns frozen dataclasses).
        # If you want these available on the model, surface them here:
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
