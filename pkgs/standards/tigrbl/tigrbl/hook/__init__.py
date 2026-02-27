"""Public hook API with lazy exports."""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS = {
    "HookSpec": "tigrbl._spec.hook_spec",
    "OpHook": "tigrbl._spec.hook_spec",
    "hook_ctx": "tigrbl.decorators.hook",
    "HOOK_DECLS_ATTR": "tigrbl.decorators.hook",
    "PHASE": "tigrbl.hook.types",
    "PHASES": "tigrbl.hook.types",
    "HookPhase": "tigrbl.hook.types",
    "HookPredicate": "tigrbl.hook.types",
    "Ctx": "tigrbl.hook.types",
    "StepFn": "tigrbl.hook.types",
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
