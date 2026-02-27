from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS = {
    "Op": "tigrbl._concrete._op",
    "OpSpec": "tigrbl._spec.op_spec",
    "get_registry": "tigrbl._concrete._op_registry",
    "OpspecRegistry": "tigrbl._concrete._op_registry",
    "alias": "tigrbl.decorators.op",
    "alias_ctx": "tigrbl.decorators.op",
    "op_alias": "tigrbl.decorators.op",
    "op_ctx": "tigrbl.decorators.op",
    "Arity": "tigrbl.op.types",
    "PersistPolicy": "tigrbl.op.types",
    "TargetOp": "tigrbl.op.types",
    "VerbAliasPolicy": "tigrbl.op.types",
    "PHASE": "tigrbl.runtime.hook_types",
    "HookPhase": "tigrbl.runtime.hook_types",
    "PHASES": "tigrbl.runtime.hook_types",
    "Ctx": "tigrbl.runtime.hook_types",
    "StepFn": "tigrbl.runtime.hook_types",
    "HookPredicate": "tigrbl.runtime.hook_types",
    "OpHook": "tigrbl._spec.hook_spec",
    "resolve": "tigrbl.mapping.op_resolver",
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
