"""Core router surfaces for the Tigrbl package."""

from __future__ import annotations

from typing import Any

__all__ = ["RouterSpec", "Router", "Route", "TigrblRouter"]


def __getattr__(name: str) -> Any:
    if name == "RouterSpec":
        from .router_spec import RouterSpec

        return RouterSpec
    if name == "Router":
        from ._router import Router

        return Router
    if name == "Route":
        from ._route import Route

        return Route
    if name == "TigrblRouter":
        from .tigrbl_router import TigrblRouter

        return TigrblRouter
    raise AttributeError(name)
