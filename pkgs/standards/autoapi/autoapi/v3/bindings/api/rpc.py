from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any, Dict, Optional, Union

from .common import ApiLike, _ensure_api_ns
from ...engine import resolver as _resolver

logger = logging.getLogger(__name__)


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
    _ensure_api_ns(api)

    if isinstance(model_or_name, str):
        mdl = api.models.get(model_or_name)
        if mdl is None:
            raise KeyError(f"Unknown model '{model_or_name}'")
    else:
        mdl = model_or_name

    fn = getattr(getattr(mdl, "rpc", SimpleNamespace()), method, None)
    if fn is None:
        raise AttributeError(
            f"{getattr(mdl, '__name__', mdl)} has no RPC method '{method}'"
        )

    # Acquire DB if not explicitly provided (op > model > api > app)
    _release_db = None
    if db is None:
        try:
            db, _release_db = _resolver.acquire(api=api, model=mdl, op_alias=method)
        except Exception:
            logger.exception(
                "DB acquire failed for rpc_call %s.%s; no default configured?",
                getattr(mdl, "__name__", mdl),
                method,
            )
            raise

    try:
        return await fn(payload, db=db, request=request, ctx=ctx)
    finally:
        if _release_db is not None:
            try:
                _release_db()
            except Exception:
                logger.debug(
                    "Non-fatal: error releasing acquired DB session (rpc_call)",
                    exc_info=True,
                )
