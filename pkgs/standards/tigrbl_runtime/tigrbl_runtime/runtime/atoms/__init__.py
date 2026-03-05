"""Compatibility bridge for legacy ``tigrbl_runtime.runtime.atoms`` imports."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any

_atoms_root = import_module("tigrbl_atoms")

__path__: list[str] = []
for _base in getattr(_atoms_root, "__path__", ()):
    _candidate = Path(_base) / "atoms"
    if _candidate.exists():
        __path__.append(str(_candidate))

__all__: list[str] = []


def __getattr__(name: str) -> Any:
    target = import_module("tigrbl_atoms.atoms")
    return getattr(target, name)
