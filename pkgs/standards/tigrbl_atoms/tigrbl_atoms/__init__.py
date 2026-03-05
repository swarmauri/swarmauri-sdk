"""Compatibility facade for legacy ``tigrbl_atoms`` imports."""

from __future__ import annotations

from importlib import import_module
import sys


def _optional_import(path: str):
    try:
        return import_module(path)
    except Exception:
        return None


_ALIASES = {
    "events": "tigrbl_kernel.kernel.events",
    "opview": "tigrbl_runtime.runtime.opview",
    "system": "tigrbl_runtime.runtime.system",
    "status": "tigrbl_runtime.runtime.status",
    "runtime": "tigrbl_runtime.runtime",
    "core": "tigrbl_core.core",
    "mapping": "tigrbl_canon.mapping",
    "_concrete": "tigrbl_concrete._concrete",
    "shortcuts": "tigrbl.shortcuts",
    "vendor": "tigrbl.vendor",
    "security": "tigrbl.security",
    "gw": "tigrbl_runtime.runtime.gw",
}

for alias, target in _ALIASES.items():
    module = _optional_import(target)
    if module is not None:
        sys.modules.setdefault(f"{__name__}.{alias}", module)
