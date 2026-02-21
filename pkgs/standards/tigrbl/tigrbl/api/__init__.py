"""Core API surfaces for the Tigrbl package."""

from __future__ import annotations

from typing import Any

__all__ = ["Router", "TigrblRouter", "TigrblApi"]


def __getattr__(name: str) -> Any:
    if name == "Router":
        from ._router import Router

        return Router
    if name == "TigrblRouter":
        from .tigrbl_router import TigrblRouter

        return TigrblRouter
    if name == "TigrblApi":
        from .tigrbl_router import TigrblRouter

        return TigrblRouter
    raise AttributeError(name)
