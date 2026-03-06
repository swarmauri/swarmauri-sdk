"""Compatibility exports for legacy ``tigrbl.specs`` imports.

Prefer importing from :mod:`tigrbl._spec` and :mod:`tigrbl.shortcuts.column`
going forward.
"""

from __future__ import annotations

from ._spec import ColumnSpec, F, IO, S, acol, makeColumn, makeVirtualColumn, vcol
from ._spec.io_spec import Pair
from ._spec.storage_spec import ForeignKeySpec

Fk = ForeignKeySpec

__all__ = [
    "ColumnSpec",
    "F",
    "IO",
    "S",
    "acol",
    "vcol",
    "Pair",
    "ForeignKeySpec",
    "Fk",
    "makeColumn",
    "makeVirtualColumn",
    "is_virtual",
]


def is_virtual(spec: ColumnSpec) -> bool:
    """Return ``True`` for wire-only columns that are not persisted."""
    return getattr(spec, "storage", None) is None
