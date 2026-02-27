"""Base class implementations for tigrbl internals."""

from ._hook import HookBase
from ._storage import ForeignKeyBase
from ._table_base import TableBase

__all__ = ["HookBase", "ForeignKeyBase", "TableBase"]
