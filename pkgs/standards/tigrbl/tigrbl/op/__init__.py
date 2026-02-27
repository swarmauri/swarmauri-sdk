"""Public operation API with lazy exports to avoid import cycles."""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS = {
    # core spec and operation descriptor
    "OpSpec": "tigrbl._spec.op_spec",
    "Op": "tigrbl._concrete._op",
    # operation types
    "PersistPolicy": "tigrbl.op.types",
    "Arity": "tigrbl.op.types",
    "TargetOp": "tigrbl.op.types",
    "VerbAliasPolicy": "tigrbl.op.types",
    "PHASE": "tigrbl.op.types",
    "HookPhase": "tigrbl.op.types",
    "PHASES": "tigrbl.op.types",
    "Ctx": "tigrbl.op.types",
    "StepFn": "tigrbl.op.types",
    "HookPredicate": "tigrbl.op.types",
    "EngineCfg": "tigrbl.op.types",
    "OpHook": "tigrbl.op.types",
    "CANON": "tigrbl.op.types",
    # decorators
    "alias": "tigrbl.decorators.op",
    "alias_ctx": "tigrbl.decorators.op",
    "op_alias": "tigrbl.decorators.op",
    "op_ctx": "tigrbl.decorators.op",
    # operation collection / resolver
    "apply_alias": "tigrbl.op.collect",
    "collect": "tigrbl.op.collect",
    "resolve": "tigrbl.mapping.op_resolver",
    # registry
    "OpspecRegistry": "tigrbl._concrete._op_registry",
    "get_registry": "tigrbl._concrete._op_registry",
    "register_ops": "tigrbl._concrete._op_registry",
    "get_registered_ops": "tigrbl._concrete._op_registry",
    "clear_registry": "tigrbl._concrete._op_registry",
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
