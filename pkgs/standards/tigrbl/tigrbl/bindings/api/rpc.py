from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any, Dict, Mapping, Optional, Union

from .common import ApiLike, _ensure_api_ns
from ...engine import resolver as _resolver
from ...core.crud.helpers.model import _single_pk_name

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/api/rpc")


async def rpc_call(
    api: ApiLike,
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
    _ensure_api_ns(api)

    if isinstance(model_or_name, str):
        mdl = api.models.get(model_or_name)
        if mdl is None:
            logger.debug("Unknown model name '%s'", model_or_name)
            raise KeyError(f"Unknown model '{model_or_name}'")
        logger.debug("Resolved model name '%s' to %s", model_or_name, mdl)
    else:
        mdl = model_or_name
        logger.debug("Using model class %s", getattr(mdl, "__name__", mdl))

    fn = getattr(getattr(mdl, "rpc", SimpleNamespace()), method, None)
    if fn is None:
        logger.debug(
            "RPC method '%s' not found on %s", method, getattr(mdl, "__name__", mdl)
        )
        raise AttributeError(
            f"{getattr(mdl, '__name__', mdl)} has no RPC method '{method}'"
        )

    # Acquire DB if not explicitly provided (op > model > api > app)
    _release_db = None
    if db is None:
        try:
            logger.debug(
                "Acquiring DB for rpc_call %s.%s", getattr(mdl, "__name__", mdl), method
            )
            db, _release_db = _resolver.acquire(api=api, model=mdl, op_alias=method)
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
        return await fn(payload, db=db, request=request, ctx=ctx_dict)
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
