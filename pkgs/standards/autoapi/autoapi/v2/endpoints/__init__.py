"""Diagnostic and RPC endpoints for the AutoAPI framework."""

__all__ = ["attach_health_and_methodz", "build_rpcdispatch"]

from .endpoints import attach_health_and_methodz
from .rpcdispatcher import build_rpcdispatch
