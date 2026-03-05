"""Compatibility facade for legacy ``tigrbl_runtime.*`` imports."""

from __future__ import annotations

from importlib import import_module
import sys
from typing import Any

_runtime = import_module("tigrbl_runtime.runtime")

_ALIASES = {
    "hook_types": "tigrbl_runtime.runtime.hook_types",
    "executor": "tigrbl_runtime.runtime.executor",
    "status": "tigrbl_runtime.runtime.status",
    "events": "tigrbl_runtime.runtime.events",
    "system": "tigrbl_runtime.runtime.system",
    "kernel": "tigrbl_runtime.runtime.kernel",
    "context": "tigrbl_runtime.runtime.context",
    "mapping": "tigrbl_canon.mapping",
    "opview": "tigrbl_runtime.runtime.opview",
}

for alias, target in _ALIASES.items():
    try:
        module = import_module(target)
    except Exception:
        continue
    sys.modules.setdefault(f"{__name__}.{alias}", module)

__all__ = list(getattr(_runtime, "__all__", ()))


def __getattr__(name: str) -> Any:
    return getattr(_runtime, name)
