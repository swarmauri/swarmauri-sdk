# autoapi/v3/opspec/__init__.py
"""
AutoAPI v3 – OpSpec package.

Public surface (re-exports):

Types:
  - OpSpec, OpHook
  - TargetOp, Arity, PersistPolicy
  - HookPhase, PHASES
  - VerbAliasPolicy

Collection & Registry:
  - resolve(model)                        → list[OpSpec]
  - get_registry(model)                   → OpspecRegistry
  - register_ops(model, specs)            → set[(alias, target)]
  - get_registered_ops(model)             → tuple[OpSpec, ...]
  - clear_registry(model)                 → None

Decorators (moved):
  The legacy decorators under `autoapi.v3.opspec.decorators` are no longer supported.
  Use the ctx-only decorators in `autoapi.v3.decorators` instead:
    • alias_ctx(...)
    • op_ctx(...)
    • hook_ctx(...)

Notes on phases (align with runtime.executor.PHASES):
  PRE_* phases run before the handler; POST_* after; ON_*_ERROR on failures; and
  transaction boundaries are modeled as START_TX / END_TX where applicable.
"""

from __future__ import annotations

# Core types
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


__all__ = [
    # types
    "OpSpec",
    "OpHook",
    "TargetOp",
    "Arity",
    "PersistPolicy",
    "PHASE",
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
]
