"""AutoAPI v3 op package."""

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
from .collect import (
    collect_decorated_ops,
    alias_map_for,
    apply_alias,
)
from .resolver import resolve
from .model_registry import (
    OpspecRegistry,
    get_registry,
    register_ops,
    get_registered_ops,
    clear_registry,
)
from .decorators import alias, alias_ctx, op_alias, op_ctx

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
    "alias_map_for",
    "apply_alias",
    "OpspecRegistry",
    "get_registry",
    "register_ops",
    "get_registered_ops",
    "clear_registry",
    "alias",
    "alias_ctx",
    "op_alias",
    "op_ctx",
]
