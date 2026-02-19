"""Core router surfaces for the Tigrbl package."""

from __future__ import annotations

from typing import Any

__all__ = ["Api", "TigrblRouter", "TigrblRouter"]


def __getattr__(name: str) -> Any:
    if name == "Api":
        from ._api import Api

        return Api
    if name == "TigrblRouter":
        from .tigrbl_router import TigrblRouter

        return TigrblRouter
    if name == "TigrblRouter":  # backwards compatibility
        from .tigrbl_router import TigrblRouter

        return TigrblRouter
    raise AttributeError(name)
