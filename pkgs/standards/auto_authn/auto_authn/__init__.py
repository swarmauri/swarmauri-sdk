"""Swarmauri auto-authn package."""

from importlib import import_module
from types import ModuleType


def __getattr__(name: str) -> ModuleType:
    if name in {"v2", "v3"}:
        return import_module(f"{__name__}.{name}")
    raise AttributeError(name)


__all__ = ["v2", "v3"]
