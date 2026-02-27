"""Backward-compatible TableBase export for ORM tables."""

from ..._base._table_base import TableBase

Base = TableBase

__all__ = ["TableBase", "Base"]
