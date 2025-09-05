"""Router builders for REST bindings."""

from .builder import _build_router
from .attach import build_router_and_attach

__all__ = ["_build_router", "build_router_and_attach"]
