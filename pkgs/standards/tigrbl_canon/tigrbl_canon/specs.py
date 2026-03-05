"""Compatibility exports for legacy ``tigrbl_canon.specs`` imports."""

from __future__ import annotations

from tigrbl_core._spec.column_spec import ColumnSpec

__all__ = ["ColumnSpec", "is_virtual"]


def is_virtual(spec: ColumnSpec) -> bool:
    return getattr(spec, "storage", None) is None
