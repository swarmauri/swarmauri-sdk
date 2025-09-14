# tigrbl/v3/specs.py
"""Compatibility layer that re-exports column specs.

Importing from ``tigrbl.specs`` remains supported but the
implementation now lives under :mod:`tigrbl.column`.
"""

from __future__ import annotations

import sys

from .column import *  # noqa: F401,F403
from .column import (
    __all__ as _all,
    column_spec as _column_spec,
    field_spec as _field_spec,
    infer as _infer,
    io_spec as _io_spec,
    shortcuts as _shortcuts,
    storage_spec as _storage_spec,
)

__all__ = list(_all)

# Allow submodule imports like ``tigrbl.specs.storage_spec``
__path__: list[str] = []
_mod = sys.modules[__name__]
_mod.column_spec = _column_spec
_mod.field_spec = _field_spec
_mod.infer = _infer
_mod.io_spec = _io_spec
_mod.shortcuts = _shortcuts
_mod.storage_spec = _storage_spec

sys.modules[f"{__name__}.column_spec"] = _column_spec
sys.modules[f"{__name__}.field_spec"] = _field_spec
sys.modules[f"{__name__}.infer"] = _infer
sys.modules[f"{__name__}.io_spec"] = _io_spec
sys.modules[f"{__name__}.shortcuts"] = _shortcuts
sys.modules[f"{__name__}.storage_spec"] = _storage_spec


def __dir__() -> list[str]:
    return sorted(__all__)
