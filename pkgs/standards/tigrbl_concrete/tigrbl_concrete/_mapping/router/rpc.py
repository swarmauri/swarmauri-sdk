from __future__ import annotations

import logging
from uuid import UUID
from types import SimpleNamespace
from typing import Any, Dict, Mapping, Optional, Union

from .common import RouterLike, _ensure_router_ns
from ..._concrete import engine_resolver as _resolver
from tigrbl_ops_oltp.crud.helpers.model import _coerce_pk_value, _single_pk_name
from tigrbl_ops_oltp.crud import ops as _crud_ops
from ..._mapping.op_resolver import resolve as resolve_ops
from tigrbl_runtime.runtime.executor.invoke import invoke_op

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/mapping/router/rpc")


def _jsonify_ids(value: Any) -> Any:
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Mapping):
        return {k: _jsonify_ids(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_jsonify_ids(v) for v in value]
    if isinstance(value, tuple):
        return tuple(_jsonify_ids(v) for v in value)
    return value


def _fallback_resolution(
    router: RouterLike, model_or_name: Union[type, str], alias: str
) -> SimpleNamespace:
    if isinstance(model_or_name, type):
        model = model_or_name
    else:
        tables = getattr(router, "tables", {}) or {}
        model = tables.get(model_or_name)
    if model is None:
        raise AttributeError(f"Unknown model '{model_or_name}'")

    specs = resolve_ops(model)
    spec = next((sp for sp in specs if sp.alias == alias), None)
    target = spec.target if spec is not None else alias
    return SimpleNamespace(model=model, target=target)


async def rpc_call(
    router: RouterLike,
    model_or_name: Union[type, str],
    method: str,
    payload: Any = None,
    *,
    db: Any | None = None,
    request: Any = None,
    ctx: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Call a registered RPC method by (model, method) pair.
    `model_or_name` may be a model class or its name.
    """
    logger.debug("rpc_call invoked for model=%s method=%s", model_or_name, method)
    _ensure_router_ns(router)

    resolution = _fallback_resolution(router, model_or_name, method)
    mdl = resolution.model
    logger.debug(
        "Resolved operation model=%s alias=%s target=%s",
        getattr(mdl, "__name__", mdl),
        method,
        resolution.target,
    )

    fn = getattr(getattr(mdl, "rpc", SimpleNamespace()), method, None)
    if fn is None:
        logger.debug(
            "RPC method '%s' not found on %s", method, getattr(mdl, "__name__", mdl)
        )
        raise AttributeError(
            f"{getattr(mdl, '__name__', mdl)} has no RPC method '{method}'"
        )

    # Acquire DB if not explicitly provided (op > model > router > app)
    _release_db = None
    if db is None:
        try:
            logger.debug(
                "Acquiring DB for rpc_call %s.%s", getattr(mdl, "__name__", mdl), method
            )
            db, _release_db = _resolver.acquire(
                router=router, model=mdl, op_alias=method
            )
        except Exception:
            logger.exception(
                "DB acquire failed for rpc_call %s.%s; no default configured?",
                getattr(mdl, "__name__", mdl),
                method,
            )
            raise
    else:
        logger.debug(
            "Using provided DB for rpc_call %s.%s",
            getattr(mdl, "__name__", mdl),
            method,
        )

    # Ensure execution context contains basic runtime metadata. In tests or
    # other direct calls there may be no ``request`` object to supply an app
    # reference, which the runtime uses to resolve the opview. When absent, the
    # kernel falls back to cached specs for the given model and alias.
    ctx_dict: Dict[str, Any] = dict(ctx or {})
    # Opportunistically derive path params from the payload when the caller
    # supplies the primary key in the body. Many RPC handlers expect the
    # identifier via ``ctx['path_params']`` (mirroring REST semantics), but
    # test code invokes ``rpc_call`` directly with the id embedded in the
    # payload.  Normalizing here preserves backwards compatibility and keeps
    # default CRUD handlers happy.
    try:
        pk_name = _single_pk_name(mdl)
    except Exception:  # model may not be bound to a table
        pk_name = None

    if pk_name and isinstance(payload, Mapping) and pk_name in payload:
        payload = dict(payload)
        payload[pk_name] = _coerce_pk_value(mdl, payload[pk_name])

    if pk_name and isinstance(payload, (list, tuple)):
        normalized_payload: list[Any] = []
        changed = False
        for item in payload:
            if isinstance(item, Mapping) and pk_name in item:
                row = dict(item)
                row[pk_name] = _coerce_pk_value(mdl, row[pk_name])
                normalized_payload.append(row)
                changed = True
            else:
                normalized_payload.append(item)
        if changed:
            payload = normalized_payload

    if pk_name and isinstance(payload, Mapping) and pk_name in payload:
        coerced_pk = _coerce_pk_value(mdl, payload[pk_name])
        pp = dict(ctx_dict.get("path_params", {}))
        pp.setdefault(pk_name, coerced_pk)
        ctx_dict["path_params"] = pp

    if pk_name and isinstance(ctx_dict.get("path_params"), Mapping):
        pp = dict(ctx_dict.get("path_params", {}))
        if pk_name in pp:
            pp[pk_name] = _coerce_pk_value(mdl, pp[pk_name])
            ctx_dict["path_params"] = pp

    if method == "bulk_delete" and pk_name and isinstance(payload, (list, tuple)):
        payload = [_coerce_pk_value(mdl, ident) for ident in payload]

    try:
        logger.debug("Executing rpc_call %s.%s", getattr(mdl, "__name__", mdl), method)
        result = await fn(payload, db=db, request=request, ctx=ctx_dict)
        if isinstance(result, Mapping) and {
            "model",
            "alias",
            "ctx",
            "serialize",
            "request",
            "db",
        }.issubset(result.keys()):
            invoke_ctx: Dict[str, Any] = dict(result["ctx"])
            invoke_ctx["response_serializer"] = result["serialize"]
            final = await invoke_op(
                request=result["request"],
                db=result["db"],
                model=result["model"],
                alias=result["alias"],
                ctx=invoke_ctx,
            )

            if not isinstance(
                final, (Mapping, list, tuple, str, int, float, bool, type(None))
            ):
                inner = getattr(final, "result", None)
                if inner is not None and inner is not final:
                    final = inner

            serializer = result.get("serialize")
            if callable(serializer):
                try:
                    final = serializer(final)
                except Exception:
                    logger.debug("rpc output serialization fallback", exc_info=True)

            if (
                isinstance(final, Mapping)
                and {"status_code", "headers", "body"}.issubset(final)
                and final.get("body") is None
                and method in {"read", "update", "replace"}
                and pk_name
            ):
                ident = (
                    (ctx_dict.get("path_params") or {}).get(pk_name)
                    if isinstance(ctx_dict.get("path_params"), Mapping)
                    else None
                )
                if ident is None and isinstance(payload, Mapping):
                    ident = payload.get(pk_name)
                ident = _coerce_pk_value(mdl, ident)
                if method == "read":
                    recovered = await _crud_ops.read(mdl, ident, db)
                elif method == "update":
                    recovered = await _crud_ops.update(mdl, ident, payload or {}, db)
                else:
                    recovered = await _crud_ops.replace(mdl, ident, payload or {}, db)
                if callable(serializer):
                    return _jsonify_ids(serializer(recovered))
                return _jsonify_ids(recovered)

            if getattr(resolution, "target", None) == "list" and isinstance(
                final, Mapping
            ):
                items = final.get("items")
                if isinstance(items, list):
                    return items
            return _jsonify_ids(final)
        return result
    finally:
        if _release_db is not None:
            try:
                _release_db()
                logger.debug(
                    "Released DB for rpc_call %s.%s",
                    getattr(mdl, "__name__", mdl),
                    method,
                )
            except Exception:
                logger.debug(
                    "Non-fatal: error releasing acquired DB session (rpc_call)",
                    exc_info=True,
                )
