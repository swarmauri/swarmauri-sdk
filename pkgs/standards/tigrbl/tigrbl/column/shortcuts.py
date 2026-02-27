"""Backward-compatible column shortcut exports."""

from ..shortcuts.column import acol, makeColumn, makeVirtualColumn, vcol
from .._spec.field_spec import FieldSpec as F
from .._spec.io_spec import IOSpec as IO
from .._spec.storage_spec import StorageSpec as S

__all__ = [  # Back-compat names expected by legacy tests/imports.
    "makeColumn",
    "makeVirtualColumn",
    "acol",
    "vcol",
    "F",
    "IO",
    "S",
]
