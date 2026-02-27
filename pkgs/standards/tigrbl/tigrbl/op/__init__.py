from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS = {
    "Op": "tigrbl._concrete._op",
    "OpSpec": "tigrbl._spec.op_spec",
    "get_registry": "tigrbl._concrete._op_registry",
    "TargetOp": "tigrbl.op.types",
    "Arity": "tigrbl.op.types",
    "PersistPolicy": "tigrbl.op.types",
    "PHASE": "tigrbl.op.types",
    "HookPhase": "tigrbl.op.types",
    "PHASES": "tigrbl.op.types",
    "apply_alias": "tigrbl.op.collect",
    "collect": "tigrbl.op.collect",
    "alias_ctx": "tigrbl.decorators.op",
    "op_ctx": "tigrbl.decorators.op",
    "alias": "tigrbl.decorators.op",
    "op_alias": "tigrbl.decorators.op",
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
