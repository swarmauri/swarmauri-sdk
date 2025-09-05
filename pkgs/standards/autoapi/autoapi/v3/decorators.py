"""Compatibility layer for decorator imports."""

from __future__ import annotations

from .op.decorators import *  # noqa: F401,F403
from .hook.decorators import *  # noqa: F401,F403
from .schema.decorators import schema_ctx
from .engine.decorators import engine_ctx
from .op.collect import collect_decorated_ops, alias_map_for, apply_alias
from .hook.collect import collect_decorated_hooks
from .op.decorators import __all__ as _op_all
from .hook.decorators import __all__ as _hook_all

__all__ = [
    *_op_all,
    *_hook_all,
    "schema_ctx",
    "engine_ctx",
    "collect_decorated_ops",
    "collect_decorated_hooks",
    "alias_map_for",
    "apply_alias",
]
