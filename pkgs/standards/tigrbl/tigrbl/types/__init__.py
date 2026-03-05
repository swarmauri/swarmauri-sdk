"""Compatibility package for legacy ``tigrbl.types`` imports."""

from __future__ import annotations

from importlib import import_module

_TARGET = import_module("tigrbl_typing.types")

__path__ = getattr(_TARGET, "__path__", [])
__all__ = list(getattr(_TARGET, "__all__", ()))

for _name in __all__:
    globals()[_name] = getattr(_TARGET, _name)
