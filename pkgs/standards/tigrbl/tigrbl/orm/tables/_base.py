"""Primary TableBase export for ORM tables."""

from ..._concrete._table import Table as TableBase

Base = TableBase

__all__ = ["TableBase", "Base"]
