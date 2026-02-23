"""Core API surfaces for the Tigrbl package."""

from __future__ import annotations

from typing import Any

from .decorators import route_ctx

__all__ = ["Router", "TigrblRouter", "route_ctx"]


def __getattr__(name: str) -> Any:
    if name == "Router":
        from ._router import Router

        return Router
    if name == "TigrblRouter":
        from .tigrbl_router import TigrblRouter

        return TigrblRouter
    if name == "route_ctx":
        return route_ctx
    raise AttributeError(name)
