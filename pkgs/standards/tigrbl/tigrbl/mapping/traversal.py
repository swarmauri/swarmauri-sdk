"""Unified traversal helpers for first-class tigrbl objects.

This module centralizes `mro_collect`, resolver access, and install flows so
callers do not need to stitch these concerns across app/table modules.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping

from .._concrete._engine import (
    collect_engine_bindings,
    install_engine_bindings,
    install_from_objects,
)
from .app_mro_collect import mro_collect_app_spec
from .column_mro_collect import mro_collect_columns
from .hook_mro_collect import mro_collect_decorated_hooks
from .op_mro_collect import mro_collect_decorated_ops
from .router_mro_collect import mro_collect_router_hooks
from .table_mro_collect import mro_collect_table_spec
from .engine_resolver import register_op, register_router, register_table, set_default


MRO_COLLECTORS: Mapping[str, Callable[..., Any]] = {
    "app": mro_collect_app_spec,
    "table": mro_collect_table_spec,
    "column": mro_collect_columns,
    "op": mro_collect_decorated_ops,
    "hook": mro_collect_decorated_hooks,
    "router": mro_collect_router_hooks,
}

RESOLVERS: Mapping[str, Mapping[str, Callable[..., Any]]] = {
    "engine": {
        "set_default": set_default,
        "register_router": register_router,
        "register_table": register_table,
        "register_op": register_op,
    }
}

INSTALLS: Mapping[str, Callable[..., Any]] = {
    "collect": collect_engine_bindings,
    "install": install_engine_bindings,
    "install_from_objects": install_from_objects,
}


__all__ = [
    "MRO_COLLECTORS",
    "RESOLVERS",
    "INSTALLS",
    "collect_engine_bindings",
    "install_engine_bindings",
    "install_from_objects",
]
