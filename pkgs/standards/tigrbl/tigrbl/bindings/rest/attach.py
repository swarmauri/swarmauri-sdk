from __future__ import annotations
import logging

from types import SimpleNamespace
from typing import Any, Optional, Sequence

from .common import OpSpec, _Key
from .router import _build_router

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/rest/attach")


def build_router_and_attach(
    model: type,
    specs: Sequence[OpSpec],
    *,
    api: Any | None = None,
    only_keys: Optional[Sequence[_Key]] = None,
) -> None:
    """
    Build a Router for the model and attach it to `model.rest.router`.
    For simplicity and correctness with FastAPI, we **rebuild the entire router**
    on each call (FastAPI does not support removing individual routes cleanly).
    """
    router = _build_router(model, specs, api=api)
    rest_ns = getattr(model, "rest", None) or SimpleNamespace()
    rest_ns.router = router
    setattr(model, "rest", rest_ns)
    logger.debug(
        "rest: %s router attached with %d routes",
        model.__name__,
        len(getattr(router, "routes", []) or []),
    )
