"""Runtime public API with lazy imports to avoid circular startup."""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS = {
    "_invoke": "executor",
    "_Ctx": "executor",
    "Kernel": "kernel",
    "build_phase_chains": "kernel",
    "get_cached_specs": "kernel",
    "_default_kernel": "kernel",
    "status": "status",
    "context": "context",
    "STEP_KINDS": "labels",
    "DOMAINS": "labels",
}

__all__ = list(_EXPORTS)


def __getattr__(name: str) -> Any:
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(name)
    module = import_module(f"{__name__}.{module_name}")
    value = getattr(module, name)
    globals()[name] = value
    return value
