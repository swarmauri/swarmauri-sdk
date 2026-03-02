"""Compatibility exports for legacy ``tigrbl.specs`` imports.

Prefer importing from :mod:`tigrbl._spec` and :mod:`tigrbl.shortcuts.column`
going forward.
"""

from __future__ import annotations

from ._spec import ColumnSpec, F, IO, S, acol, makeColumn, makeVirtualColumn, vcol

__all__ = [
    "ColumnSpec",
    "F",
    "IO",
    "S",
    "acol",
    "vcol",
    "makeColumn",
    "makeVirtualColumn",
    "is_virtual",
]


def is_virtual(spec: ColumnSpec) -> bool:
    """Return ``True`` for wire-only columns that are not persisted."""
    return getattr(spec, "storage", None) is None
