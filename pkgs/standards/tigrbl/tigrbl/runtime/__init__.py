"""Runtime public API kept import-light to avoid startup cycles."""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS = {
    "_invoke": "tigrbl.runtime.executor",
    "_Ctx": "tigrbl.runtime.executor",
    "Kernel": "tigrbl.runtime.kernel",
    "build_phase_chains": "tigrbl.runtime.kernel",
    "run": "tigrbl.runtime.kernel",
    "get_cached_specs": "tigrbl.runtime.kernel",
    "_default_kernel": "tigrbl.runtime.kernel",
    "events": "tigrbl.runtime.events",
    "status": "tigrbl.runtime.status",
    "context": "tigrbl.runtime.context",
    "STEP_KINDS": "tigrbl.runtime.labels",
    "DOMAINS": "tigrbl.runtime.labels",
}

__all__ = list(_EXPORTS)


def __getattr__(name: str) -> Any:
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(name)
    module = import_module(module_name)
    value = getattr(module, name)
    globals()[name] = value
    return value
