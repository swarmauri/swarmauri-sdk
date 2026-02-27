from __future__ import annotations

from ..shortcuts.column import (
    F,
    IO,
    S,
    Column,
    ColumnSpec,
    acol,
    makeColumn,
    makeVirtualColumn,
    vcol,
)


def is_virtual(spec: ColumnSpec | Column) -> bool:
    if isinstance(spec, Column):
        spec = spec.spec
    return spec.storage is None


__all__ = [
    "Column",
    "ColumnSpec",
    "F",
    "IO",
    "S",
    "makeColumn",
    "makeVirtualColumn",
    "acol",
    "vcol",
    "is_virtual",
]
