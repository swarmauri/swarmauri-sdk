"""AutoAPI v3 – Op package."""

from __future__ import annotations

from ._op import Op
from .types import (
    OpSpec,
    OpHook,
    TargetOp,
    Arity,
    PersistPolicy,
    PHASE,
    HookPhase,
    PHASES,
    VerbAliasPolicy,
)
from .collect import resolve, collect_decorated_ops
from .model_registry import (
    OpspecRegistry,
    get_registry,
    register_ops,
    get_registered_ops,
    clear_registry,
)

__all__ = [
    "Op",
    "OpSpec",
    "OpHook",
    "TargetOp",
    "Arity",
    "PersistPolicy",
    "PHASE",
    "HookPhase",
    "PHASES",
    "VerbAliasPolicy",
    "resolve",
    "collect_decorated_ops",
    "OpspecRegistry",
    "get_registry",
    "register_ops",
    "get_registered_ops",
    "clear_registry",
]
