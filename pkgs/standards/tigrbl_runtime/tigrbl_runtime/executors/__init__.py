"""Executor public API with lazy imports to avoid circular startup."""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS = {
    "ExecutorBase": "base",
    "PhaseExecutor": "phase",
    "PackedPlanExecutor": "packed",
    "NumbaPackedPlanExecutor": "numba_packed",
    "_Ctx": "types",
    "_invoke": "invoke",
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
