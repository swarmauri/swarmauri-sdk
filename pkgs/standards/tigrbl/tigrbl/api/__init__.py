"""Core API surfaces for the Tigrbl package."""

from __future__ import annotations

from typing import Any

__all__ = ["Api", "TigrblApi"]


def __getattr__(name: str) -> Any:
    if name == "Api":
        from ._api import Api

        return Api
    if name == "TigrblApi":
        from .tigrbl_api import TigrblApi

        return TigrblApi
    raise AttributeError(name)
