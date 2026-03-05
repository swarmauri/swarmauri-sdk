"""Compatibility bridge for legacy ``tigrbl_canon._concrete`` imports."""

from __future__ import annotations

from importlib import import_module
from typing import Any

_TARGET = "tigrbl_concrete._concrete"
_target_pkg = import_module(_TARGET)

__path__ = getattr(_target_pkg, "__path__", [])
__all__ = list(getattr(_target_pkg, "__all__", ()))


def __getattr__(name: str) -> Any:
    return getattr(_target_pkg, name)
