"""Compatibility shim for routing runtime helpers.

Canonical implementations now live in ``tigrbl.core.router_runtime``.
"""

from __future__ import annotations

from ..core.router_runtime import (  # noqa: F401
    _invoke_dependency,
    _resolve_handler_kwargs,
    _resolve_route_dependencies,
    call_handler,
    dispatch,
    is_metadata_route,
)

__all__ = [
    "dispatch",
    "call_handler",
    "is_metadata_route",
    "_resolve_route_dependencies",
    "_resolve_handler_kwargs",
    "_invoke_dependency",
]
