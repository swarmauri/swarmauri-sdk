"""tigrbl_concrete compatibility facade.

This package provides concrete implementations while preserving legacy
submodule paths that still live in ``tigrbl``.
"""

from __future__ import annotations

from importlib import import_module
import sys


_COMPAT_ALIASES = {
    "ddl": "tigrbl.ddl",
    "system": "tigrbl.system",
    "op": "tigrbl.op",
    "config": "tigrbl.config",
    "schema": "tigrbl.schema",
    "security": "tigrbl.security",
}


def _optional_import(path: str):
    try:
        return import_module(path)
    except ImportError:
        return None


for alias, target in _COMPAT_ALIASES.items():
    module = _optional_import(target)
    if module is not None:
        sys.modules.setdefault(f"{__name__}.{alias}", module)


def build_handlers(*args, **kwargs):
    return import_module("tigrbl_concrete._mapping.model")._materialize_handlers(
        *args, **kwargs
    )


def build_hooks(*args, **kwargs):
    return import_module("tigrbl_concrete._mapping.model")._bind_model_hooks(
        *args, **kwargs
    )


def build_schemas(*args, **kwargs):
    return import_module("tigrbl_concrete._mapping.model")._materialize_schemas(
        *args, **kwargs
    )


def build_rest_router(*args, **kwargs):
    if "router" not in kwargs:
        kwargs["router"] = None
    return import_module("tigrbl_concrete._mapping.model")._materialize_rest_router(
        *args, **kwargs
    )


__all__ = [
    "build_handlers",
    "build_hooks",
    "build_schemas",
    "build_rest_router",
]
