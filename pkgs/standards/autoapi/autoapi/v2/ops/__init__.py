# autoapi/v2/ops/__init__.py
"""
Ops facade for AutoAPI v2.

This package exposes the single source of truth for operation configuration:
- OpSpec / OpHook data structures
- Lightweight in-memory registry helpers
- Optional decorators for class/method-based declaration

Typical usage:

    from autoapi.v2.ops import OpSpec, register_ops, op_alias, custom_op

    # Imperative registration
    register_ops(Keys, [
        OpSpec(alias="rm", target="delete", table=Keys, expose_routes=False),
    ])

    # Class decorator alias
    @op_alias(alias="ls", target="list")
    class Keys(Base, OpConfigProvider):
        ...

    # Method decorator custom verb
    class Keys(Base, OpConfigProvider):
        @custom_op(alias="rotate", arity="member", persist="override")
        async def rotate(self, *, ctx, db, request, payload):
            ...
"""

from __future__ import annotations

from .spec import (
    OpSpec,
    OpHook,
    PersistPolicy,
    Arity,
    TargetOp,
    ReturnForm,
    HookFn,
)
from .registry import register_ops, get_registered_ops
from .decorators import op_alias, custom_op

__all__ = [
    "OpSpec",
    "OpHook",
    "HookFn",
    "PersistPolicy",
    "Arity",
    "TargetOp",
    "ReturnForm",
    "register_ops",
    "get_registered_ops",
    "op_alias",
    "custom_op",
]
