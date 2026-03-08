from __future__ import annotations

from .._base import ColumnBase as ColumnSpec
from .._spec.field_spec import FieldSpec as F
from .._spec.io_spec import IOSpec as IO
from .._spec.storage_spec import StorageSpec as S
from ..shortcuts.column import acol, makeColumn, makeVirtualColumn, vcol

__all__ = [
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


def is_virtual(spec: object) -> bool:
    return getattr(spec, "storage", None) is None
