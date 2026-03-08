from __future__ import annotations

from tigrbl_base._base import ColumnBase


class Column(ColumnBase):
    """Concrete SQLAlchemy column implementing a :class:`ColumnSpec`."""


__all__ = ["Column"]
