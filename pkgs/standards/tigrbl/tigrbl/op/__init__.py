from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = [
    "Op",
    "OpSpec",
    "OpspecRegistry",
    "get_registry",
    "resolve",
    "alias",
    "alias_ctx",
    "op_alias",
    "op_ctx",
    "Arity",
    "TargetOp",
    "PersistPolicy",
    "PHASE",
    "PHASES",
    "HookPhase",
]


def __getattr__(name: str) -> Any:
    if name in {"OpSpec"}:
        return import_module(".._spec.op_spec", __name__).OpSpec
    if name in {"alias", "alias_ctx", "op_alias", "op_ctx"}:
        return getattr(import_module("..decorators.op", __name__), name)
    if name in {"resolve"}:
        return import_module("..mapping.op_resolver", __name__).resolve
    if name in {"Arity", "TargetOp", "PersistPolicy"}:
        return getattr(import_module(".._spec.op_spec", __name__), name)
    if name in {"PHASE", "PHASES", "HookPhase"}:
        return getattr(import_module("..runtime.hook_types", __name__), name)
    if name == "Op":
        return import_module(".._concrete._op", __name__).Op
    if name in {"OpspecRegistry", "get_registry"}:
        return getattr(import_module(".._concrete._op_registry", __name__), name)
    raise AttributeError(name)
