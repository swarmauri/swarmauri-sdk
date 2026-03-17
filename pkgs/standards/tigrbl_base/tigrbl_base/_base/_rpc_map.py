# tigrbl/v3/mapping/rpc.py
from __future__ import annotations

import inspect
import logging
from types import SimpleNamespace
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)

from pydantic import BaseModel

from tigrbl_core._spec import OpSpec
from tigrbl_base._base import AttrDict


logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/mapping/rpc")


class RpcMapValidationError(ValueError):
    """Base-layer validation error for RPC mapping payload shapes."""

    def __init__(self, *, status_code: int, detail: dict[str, Any]):
        super().__init__(detail.get("reason", "RPC payload validation error"))
        self.status_code = status_code
        self.detail = detail


_Key = Tuple[str, str]  # (alias, target)


_WRAPPER_KEYS = frozenset({"data", "payload", "body", "item"})


def _schema_field_names(schema: Any) -> set[str]:
    """Return top-level field names declared by a Pydantic schema class."""
    if not schema or not inspect.isclass(schema) or not issubclass(schema, BaseModel):
        return set()

    fields = getattr(schema, "model_fields", None)
    if not isinstance(fields, Mapping):
        return set()

    names: set[str] = set(fields.keys())
    for field_name, field_info in fields.items():
        alias = getattr(field_info, "alias", None)
        if isinstance(alias, str) and alias:
            names.add(alias)
        validation_alias = getattr(field_info, "validation_alias", None)
        if isinstance(validation_alias, str) and validation_alias:
            names.add(validation_alias)
    return names


def _allowed_wrapper_keys(model: type, alias: str, target: str) -> set[str]:
    """Wrapper-like names that are valid operation fields for this RPC method."""
    schemas_root = getattr(model, "schemas", None)
    alias_ns = getattr(schemas_root, alias, None) if schemas_root else None
    if not alias_ns:
        return set()

    allowed = _schema_field_names(getattr(alias_ns, "in_", None))
    if target.startswith("bulk_") and target != "bulk_delete":
        allowed |= _schema_field_names(getattr(alias_ns, "in_item", None))
    return allowed & set(_WRAPPER_KEYS)


def _reject_wrapper_keys(payload: Any, *, allowed_keys: set[str] | None = None) -> None:
    allowed = allowed_keys or set()

    if isinstance(payload, Mapping):
        disallowed = sorted(
            k for k in payload if k in _WRAPPER_KEYS and k not in allowed
        )
        if disallowed:
            raise RpcMapValidationError(
                status_code=422,
                detail={
                    "reason": "Wrapper keys are not allowed; params must match the operation schema.",
                    "disallowed_keys": disallowed,
                },
            )
        return

    if isinstance(payload, Sequence) and not isinstance(payload, (str, bytes)):
        for item in payload:
            if isinstance(item, Mapping):
                _reject_wrapper_keys(item, allowed_keys=allowed)


# ───────────────────────────────────────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────────────────────────────────────


def _ns(obj: Any, name: str) -> Any:
    ns = getattr(obj, name, None)
    if ns is None:
        ns = SimpleNamespace()
        setattr(obj, name, ns)
    return ns


def _coerce_payload(payload: Any) -> Any:
    """Normalize common payload shapes.

    ``dict``-like and Pydantic models become plain ``dict``s. ``None`` becomes an
    empty ``dict``. Sequence payloads (used by bulk operations) pass through as
    lists of ``dict``s when possible; otherwise the original sequence is
    returned. Any other type yields an empty ``dict``.
    """
    if payload is None:
        return {}
    if isinstance(payload, BaseModel):
        try:
            return payload.model_dump(exclude_none=False)
        except Exception:
            return dict(payload.__dict__)
    if isinstance(payload, Mapping):
        return dict(payload)
    if isinstance(payload, Sequence) and not isinstance(payload, (str, bytes)):
        out: list[Any] = []
        for item in payload:
            if isinstance(item, BaseModel):
                try:
                    out.append(item.model_dump(exclude_none=False))
                except Exception:
                    out.append(dict(item.__dict__))
            elif isinstance(item, Mapping):
                out.append(dict(item))
            else:
                out.append(item)
        return out
    return {}


def _ensure_jsonable(obj: Any) -> Any:
    """Best-effort conversion of DB rows or ORM objects to primitives."""
    if hasattr(obj, "status_code") and hasattr(obj, "headers") and hasattr(obj, "body"):
        response_like = AttrDict(
            {
                "status_code": getattr(obj, "status_code"),
                "headers": getattr(obj, "headers"),
                "body": getattr(obj, "body"),
            }
        )
        if hasattr(obj, "media_type"):
            response_like["media_type"] = getattr(obj, "media_type")
        if hasattr(obj, "raw_headers"):
            response_like["raw_headers"] = getattr(obj, "raw_headers")
        if hasattr(obj, "body_iterator"):
            response_like["body_iterator"] = getattr(obj, "body_iterator")
        if hasattr(obj, "path"):
            response_like["path"] = getattr(obj, "path")
        if hasattr(obj, "url"):
            response_like["url"] = getattr(obj, "url")
        return response_like

    if isinstance(obj, (list, tuple)):
        return [_ensure_jsonable(x) for x in obj]
    if isinstance(obj, Mapping):
        try:
            return AttrDict({k: _ensure_jsonable(v) for k, v in dict(obj).items()})
        except Exception:
            pass
    try:
        data = vars(obj)
    except TypeError:
        return obj
    return AttrDict(
        {k: _ensure_jsonable(v) for k, v in data.items() if not k.startswith("_")}
    )


def _validate_input(
    model: type, alias: str, target: str, payload: Mapping[str, Any]
) -> Mapping[str, Any]:
    """Choose the appropriate request schema (if any) and validate/normalize payload."""
    schemas_root = getattr(model, "schemas", None)
    if not schemas_root:
        return payload
    alias_ns = getattr(schemas_root, alias, None)
    if not alias_ns:
        return payload

    in_model = getattr(alias_ns, "in_", None)

    if in_model and inspect.isclass(in_model) and issubclass(in_model, BaseModel):
        try:
            inst = in_model.model_validate(payload)  # type: ignore[arg-type]
            return inst.model_dump(exclude_none=True)
        except Exception as e:
            # Let the executor/runtime error mappers standardize later; pass original payload
            logger.debug(
                "rpc input validation failed for %s.%s: %s",
                model.__name__,
                alias,
                e,
                exc_info=True,
            )
    return payload


def _serialize_output(
    model: type,
    alias: str,
    target: str,
    result: Any,
    sp: OpSpec | None = None,
) -> Any:
    """Serialize result(s) if an OUT schema is available for the op.

    For 'list', the OUT schema represents the element shape.
    """
    del sp  # backward-compatible kwarg accepted by older callers/tests

    schemas_root = getattr(model, "schemas", None)
    if not schemas_root:
        return _ensure_jsonable(result)
    alias_ns = getattr(schemas_root, alias, None)
    if not alias_ns:
        return _ensure_jsonable(result)

    if target in {"bulk_create", "bulk_update", "bulk_replace", "bulk_merge"}:
        out_model = getattr(alias_ns, "out_item", None)
    else:
        out_model = getattr(alias_ns, "out", None)

    if (
        not out_model
        or not inspect.isclass(out_model)
        or not issubclass(out_model, BaseModel)
    ):
        return _ensure_jsonable(result)

    def _dump_with_extras(value: Any) -> Any:
        raw_value = _ensure_jsonable(value)
        if isinstance(raw_value, Mapping):
            raw_mapping = dict(raw_value)
            normalized = out_model.model_validate(raw_mapping).model_dump(
                exclude_none=False, by_alias=True
            )
            normalized.update(raw_mapping)
            return normalized
        return out_model.model_validate(raw_value).model_dump(
            exclude_none=False, by_alias=True
        )

    try:
        if isinstance(result, Mapping):
            if "item" in result and isinstance(result.get("item"), Mapping):
                result = result.get("item")
            elif "result" in result and isinstance(result.get("result"), Mapping):
                result = result.get("result")

        if target == "list":
            if isinstance(result, Mapping):
                items = result.get("items")
                if isinstance(items, (list, tuple)):
                    return [_dump_with_extras(x) for x in items]
                wrapped = result.get("result")
                if isinstance(wrapped, (list, tuple)):
                    return [_dump_with_extras(x) for x in wrapped]
            if isinstance(result, (list, tuple)):
                return [_dump_with_extras(x) for x in result]
        if target in {
            "bulk_create",
            "bulk_update",
            "bulk_replace",
            "bulk_merge",
        } and isinstance(result, (list, tuple)):
            return [_dump_with_extras(x) for x in result]
        # Single object case
        return _dump_with_extras(result)
    except Exception as e:
        # If serialization fails, let raw result through rather than failing the call
        logger.debug(
            "rpc output serialization failed for %s.%s: %s",
            model.__name__,
            alias,
            e,
            exc_info=True,
        )
        return _ensure_jsonable(result)


# ───────────────────────────────────────────────────────────────────────────────
# RPC wrapper builder
# ───────────────────────────────────────────────────────────────────────────────


def _build_rpc_callable(model: type, sp: OpSpec) -> Callable[..., Awaitable[Any]]:
    """
    Create an async callable that validates payload and returns an operation
    envelope for the runtime gateway/executor.

    Signature:
        async def rpc_method(payload: Mapping | BaseModel | None = None, *, db, request=None, ctx=None) -> Any
    """
    alias = sp.alias
    target = sp.target

    async def _rpc_method(
        payload: Any = None,
        *,
        db: Any,
        request: Any = None,
        ctx: Optional[Dict[str, Any]] = None,
    ) -> Any:
        # 1) normalize + validate input
        schemas_root = getattr(model, "schemas", None)
        alias_ns = getattr(schemas_root, alias, None)
        item_in_model = getattr(alias_ns, "in_item", None)
        raw_payload = _coerce_payload(payload)
        if (
            isinstance(raw_payload, Mapping)
            and set(raw_payload.keys()) == {"params"}
            and isinstance(raw_payload.get("params"), Mapping)
        ):
            raw_payload = dict(raw_payload["params"])

        allowed_wrapper_keys = _allowed_wrapper_keys(model, alias, target)
        _reject_wrapper_keys(raw_payload, allowed_keys=allowed_wrapper_keys)

        if target == "bulk_delete" and not isinstance(raw_payload, Mapping):
            raw_payload = {"ids": raw_payload}
        if (
            target.startswith("bulk_")
            and target != "bulk_delete"
            and isinstance(raw_payload, Sequence)
        ):
            merged_payload = []
            for item in raw_payload:
                if item_in_model and isinstance(item, Mapping):
                    norm = item_in_model.model_validate(dict(item)).model_dump(
                        exclude_none=True
                    )
                    merged_payload.append({**dict(item), **norm})
                elif item_in_model:
                    norm = item_in_model.model_validate(item).model_dump(
                        exclude_none=True
                    )
                    merged_payload.append(norm)
                else:
                    merged_payload.append(item)
        else:
            norm_payload = _validate_input(model, alias, target, raw_payload)
            merged_payload = dict(raw_payload)
            for key, value in norm_payload.items():
                merged_payload[key] = value

        # 2) build execution context seed for downstream runtime execution
        base_ctx: Dict[str, Any] = dict(ctx or {})
        base_ctx.setdefault("payload", merged_payload)
        base_ctx.setdefault("db", db)
        if request is not None:
            base_ctx.setdefault("request", request)
        # surface contextual metadata for runtime atoms
        app_ref = (
            getattr(request, "app", None)
            or base_ctx.get("app")
            or getattr(model, "router", None)
            or model
        )
        base_ctx.setdefault("app", app_ref)
        base_ctx.setdefault("router", base_ctx.get("router") or app_ref)
        base_ctx.setdefault("model", model)
        base_ctx.setdefault("op", alias)
        base_ctx.setdefault("method", alias)
        base_ctx.setdefault("target", target)
        # Runtime atoms can synthesize schema metadata from column specs when
        # an opview has not been materialized on the invocation context.
        # Keep this in base so RPC calls stay independent from deprecated canon
        # opview builders.
        specs = base_ctx.get("specs")
        if not isinstance(specs, Mapping) or not specs:
            base_ctx["specs"] = getattr(model, "__tigrbl_cols__", {}) or {}
        # helpful env metadata
        base_ctx.setdefault(
            "env",
            SimpleNamespace(
                method=alias, params=merged_payload, target=target, model=model
            ),
        )

        def serialize(result: Any) -> Any:
            if result is None and target in {"update", "replace", "merge"}:
                return _ensure_jsonable(merged_payload)
            return _serialize_output(model, alias, target, result)

        base_ctx["response_serializer"] = serialize
        return AttrDict(
            {
                "model": model,
                "alias": alias,
                "target": target,
                "payload": merged_payload,
                "ctx": base_ctx,
                "serialize": serialize,
                "request": request,
                "db": db,
            }
        )

    # Give the callable a nice name for introspection/logging
    _rpc_method.__name__ = f"rpc_{model.__name__}_{alias}"
    _rpc_method.__qualname__ = _rpc_method.__name__
    _rpc_method.__doc__ = f"RPC method for {model.__name__}.{alias} ({target})"

    return _rpc_method


def _attach_one(model: type, sp: OpSpec) -> None:
    rpc_root = _ns(model, "rpc")
    fn = _build_rpc_callable(model, sp)
    setattr(rpc_root, sp.alias, fn)
    logger.debug("rpc: %s.%s registered", model.__name__, sp.alias)


# ───────────────────────────────────────────────────────────────────────────────
# Public API
# ───────────────────────────────────────────────────────────────────────────────


def _attach_model_rpc_call(model: type) -> None:
    if hasattr(model, "rpc_call") and callable(getattr(model, "rpc_call")):
        return

    async def _model_rpc_call(
        method: str,
        payload: Any = None,
        *,
        db: Any | None = None,
        request: Any = None,
        ctx: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await rpc_call(
            model,
            model,
            method,
            payload,
            db=db,
            request=request,
            ctx=ctx,
        )

    setattr(model, "rpc_call", _model_rpc_call)


def register_and_attach(
    model: type, specs: Sequence[OpSpec], *, only_keys: Optional[Sequence[_Key]] = None
) -> None:
    """
    Register async callables under `model.rpc.<alias>` for each OpSpec.
    If `only_keys` is provided, limit work to those (alias,target) pairs.
    """
    wanted = set(only_keys or ())
    attached_any = False
    for sp in specs:
        key = (sp.alias, sp.target)
        if wanted and key not in wanted:
            continue
        _attach_one(model, sp)
        attached_any = True

    if attached_any:
        _attach_model_rpc_call(model)


async def rpc_call(
    router: Any,
    model_or_name: type | str,
    method: str,
    payload: Any = None,
    *,
    db: Any | None = None,
    request: Any = None,
    ctx: Optional[Dict[str, Any]] = None,
) -> Any:
    """Compatibility RPC dispatcher for direct mapping-level calls.

    This helper resolves a model RPC callable and returns the generated
    operation envelope. Runtime execution is handled by the gateway layer.
    """
    if isinstance(model_or_name, type):
        model = model_or_name
    else:
        tables = getattr(router, "tables", {}) or {}
        model = tables.get(model_or_name)

    if model is None:
        raise AttributeError(f"Unknown model '{model_or_name}'")

    fn = getattr(getattr(model, "rpc", SimpleNamespace()), method, None)
    if fn is None:
        raise AttributeError(
            f"{getattr(model, '__name__', model)} has no RPC method '{method}'"
        )

    return await fn(payload, db=db, request=request, ctx=dict(ctx or {}))


__all__ = ["register_and_attach", "rpc_call", "RpcMapValidationError"]
