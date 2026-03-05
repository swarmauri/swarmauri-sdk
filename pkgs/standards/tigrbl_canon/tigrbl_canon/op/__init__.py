"""Compatibility namespace for legacy ``tigrbl_canon.op`` imports."""

from __future__ import annotations

from importlib import import_module
from pkgutil import extend_path
from typing import Any

__path__ = extend_path(__path__, __name__)
_TARGET = import_module("tigrbl.op")
for _path in getattr(_TARGET, "__path__", ()):
    if _path not in __path__:
        __path__.append(_path)

__all__ = list(getattr(_TARGET, "__all__", ()))


def __getattr__(name: str) -> Any:
    return getattr(_TARGET, name)

