"""Compatibility layer for decorator imports."""

from __future__ import annotations

from .op.decorators import *  # noqa: F401,F403
from .hook.decorators import *  # noqa: F401,F403
from .schema.decorators import schema_ctx
from .engine.decorators import engine_ctx
from .op.decorators import __all__ as _op_all
from .hook.decorators import __all__ as _hook_all

__all__ = [
    *_op_all,
    *_hook_all,
    "schema_ctx",
    "engine_ctx",
]
