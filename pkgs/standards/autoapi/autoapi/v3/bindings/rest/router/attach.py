"""Utilities to attach built routers to models."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Optional, Sequence, Tuple

from ..utils import logger
from .builder import _build_router
from ...ops import OpSpec

_Key = Tuple[str, str]  # (alias, target)


def build_router_and_attach(
    model: type, specs: Sequence[OpSpec], *, only_keys: Optional[Sequence[_Key]] = None
) -> None:
    """Build a Router for the model and attach it to ``model.rest.router``."""
    router = _build_router(model, specs)
    rest_ns = getattr(model, "rest", None) or SimpleNamespace()
    rest_ns.router = router
    setattr(model, "rest", rest_ns)
    logger.debug(
        "rest: %s router attached with %d routes",
        model.__name__,
        len(getattr(router, "routes", []) or []),
    )


__all__ = ["build_router_and_attach"]
