from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any, Dict, Optional, Union

from .common import ApiLike, _ensure_api_ns
from ...engine import resolver as _resolver

logging.getLogger("uvicorn").setLevel(logging.DEBUG)
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

    try:
        logger.debug("Executing rpc_call %s.%s", getattr(mdl, "__name__", mdl), method)
        seeded_ctx = dict(ctx or {})
        seeded_ctx.setdefault("app", api)
        seeded_ctx.setdefault("api", api)
        return await fn(payload, db=db, request=request, ctx=seeded_ctx)
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
