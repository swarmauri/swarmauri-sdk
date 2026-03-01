from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any, Dict, Mapping, Optional, Union

from .common import RouterLike, _ensure_router_ns
from ...mapping import engine_resolver as _resolver
from ...core.crud.helpers.model import _single_pk_name
from ...mapping.op_resolver import resolve as resolve_ops
from ...runtime.executor.invoke import _invoke

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/mapping/router/rpc")


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
    if isinstance(payload, Mapping):
        try:
            pk_name = _single_pk_name(mdl)
        except Exception:  # model may not be bound to a table
            pk_name = None
        if pk_name and pk_name in payload:
            pp = dict(ctx_dict.get("path_params", {}))
            pp.setdefault(pk_name, payload[pk_name])
            ctx_dict["path_params"] = pp

    try:
        logger.debug("Executing rpc_call %s.%s", getattr(mdl, "__name__", mdl), method)
        result = await fn(payload, db=db, request=request, ctx=ctx_dict)
        if isinstance(result, Mapping) and {
            "phases",
            "ctx",
            "serialize",
            "request",
            "db",
        }.issubset(result.keys()):
            invoke_ctx: Dict[str, Any] = dict(result["ctx"])
            invoke_ctx["response_serializer"] = result["serialize"]
            return await _invoke(
                request=result["request"],
                db=result["db"],
                phases=result["phases"],
                ctx=invoke_ctx,
            )
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
