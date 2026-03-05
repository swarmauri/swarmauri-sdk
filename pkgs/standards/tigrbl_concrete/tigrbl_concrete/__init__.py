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
