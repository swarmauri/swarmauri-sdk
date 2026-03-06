"""Compatibility exports for legacy ``tigrbl.specs`` imports.

Prefer importing from :mod:`tigrbl._spec` and :mod:`tigrbl.shortcuts.column`
going forward.
"""

from __future__ import annotations

from tigrbl_core._spec.column_spec import ColumnSpec
from tigrbl_core._spec.field_spec import FieldSpec as F
from tigrbl_core._spec.io_spec import IOSpec as IO
from tigrbl_core._spec.io_spec import Pair
from tigrbl_core._spec.storage_spec import ForeignKeySpec
from tigrbl_core._spec.storage_spec import StorageSpec as S

from .shortcuts.column import acol, makeColumn, makeVirtualColumn, vcol

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
