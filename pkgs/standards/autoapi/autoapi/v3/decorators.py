# autoapi/v3/decorators.py
"""Compatibility layer re-exporting decorators and helpers."""

from __future__ import annotations

from .op.decorators import (
    alias,
    alias_ctx,
    op_alias,
    op_ctx,
)
from .hook import hook_ctx
from .engine.decorators import engine_ctx
from .schema.decorators import schema_ctx

__all__ = [
    "alias",
    "alias_ctx",
    "op_alias",
    "op_ctx",
    "schema_ctx",
    "hook_ctx",
    "engine_ctx",
]
