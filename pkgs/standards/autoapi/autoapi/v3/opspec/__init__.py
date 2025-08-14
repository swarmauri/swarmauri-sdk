# autoapi/v3/opspec/__init__.py
"""
AutoAPI v3 – OpSpec package.

Public surface (re-exports):

Types:
  - OpSpec, OpHook
  - TargetOp, Arity, PersistPolicy, ReturnForm
  - HookPhase, PHASES
  - VerbAliasPolicy

Collection & Registry:
  - resolve(model)                        → list[OpSpec]
  - get_registry(model)                   → OpspecRegistry
  - register_ops(model, specs)            → set[(alias, target)]
  - get_registered_ops(model)             → tuple[OpSpec, ...]
  - clear_registry(model)                 → None

Decorators:
  - op_alias(...)
  - custom_op(...)

Notes on phases (align with runtime.executor):
  PRE_TX_BEGIN → START_TX → PRE_HANDLER → HANDLER → POST_HANDLER → PRE_COMMIT → END_TX → POST_COMMIT → POST_RESPONSE
  Error hooks: ON_*_ERROR, plus ON_ROLLBACK
"""

from __future__ import annotations

# Core types
from .types import (
    OpSpec,
    OpHook,
    TargetOp,
    Arity,
    PersistPolicy,
    ReturnForm,
    HookPhase,
    PHASES,
    VerbAliasPolicy,
)

# Collector
from .collect import resolve

# Per-model registry
from .model_registry import (
    OpspecRegistry,
    get_registry,
    register_ops,
    get_registered_ops,
    clear_registry,
)

# Decorators
from .decorators import op_alias, op


__all__ = [
    # types
    "OpSpec",
    "OpHook",
    "TargetOp",
    "Arity",
    "PersistPolicy",
    "ReturnForm",
    "HookPhase",
    "PHASES",
    "VerbAliasPolicy",
    # collection
    "resolve",
    # registry
    "OpspecRegistry",
    "get_registry",
    "register_ops",
    "get_registered_ops",
    "clear_registry",
    # decorators
    "op_alias",
    "op",
]
