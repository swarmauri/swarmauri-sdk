# tigrbl/v3/column/__init__.py
"""Tigrbl v3 – column specs public API.

Unifies StorageSpec (DB-facing), FieldSpec (python/wire semantics), and IOSpec (in/out exposure)
into a :class:`ColumnSpec` with a :class:`Column` descriptor. Provides ergonomic constructors
``makeColumn`` and ``makeVirtualColumn`` (with ``acol``/``vcol`` convenience aliases) and re-exports the
bind-time type inference utilities and markers.

Public surface:
    Column, ColumnSpec, FieldSpec as F, StorageSpec as S, IOSpec as IO
    makeColumn, makeVirtualColumn, acol, vcol
    infer, Inferred, DataKind, SATypePlan, JsonHint
    markers: Email, Phone
    exceptions: InferenceError, UnsupportedType
    helper: is_virtual(ColumnSpec) -> bool
"""

from __future__ import annotations

# Core spec types
from .column_spec import ColumnSpec
from ._column import Column
from .field_spec import FieldSpec as F
from .storage_spec import StorageSpec as S
from .io_spec import IOSpec as IO

# Ergonomic constructors
from .shortcuts import makeColumn, makeVirtualColumn, acol, vcol

# Bind-time inference (DB/vendor-agnostic)
from .infer import (
    infer,
    Inferred,
    DataKind,
    SATypePlan,
    JsonHint,
    Email,
    Phone,
    InferenceError,
    UnsupportedType,
)

__all__ = [
    "ColumnSpec",
    "Column",
    "F",
    "S",
    "IO",
    "makeColumn",
    "makeVirtualColumn",
    "acol",
    "vcol",
    "infer",
    "Inferred",
    "DataKind",
    "SATypePlan",
    "JsonHint",
    "Email",
    "Phone",
    "InferenceError",
    "UnsupportedType",
    "is_virtual",
]


def is_virtual(col: ColumnSpec) -> bool:
    """Return True if the column is wire-only (never persisted)."""
    return getattr(col, "storage", None) is None


def __dir__():
    return sorted(__all__)
