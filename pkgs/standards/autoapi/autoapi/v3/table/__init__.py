"""Table module exposing Base and Table."""

from __future__ import annotations

from ._base import Base
from ._table import Table
from .table_spec import TableSpec

__all__ = ["Base", "Table", "TableSpec"]
