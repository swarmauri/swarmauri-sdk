# autoapi/v3/columns/__init__.py
from __future__ import annotations
from typing import Any
from sqlalchemy.orm import MappedColumn
from ..specs import ColumnSpec


class SpecColumn(MappedColumn):
    """MappedColumn that carries AutoAPI specs as first-class attributes."""

    __slots__ = ("colspec", "io_spec", "field_spec", "storage_spec")

    def __init__(self, spec: ColumnSpec, **kw: Any) -> None:
        s = spec.storage
        super().__init__(
            s.type_,
            primary_key=s.primary_key,
            nullable=s.nullable,
            unique=s.unique,  # triggers named UniqueConstraint via naming_convention
            index=s.index,  # auto Index
            server_default=s.server_default,
            onupdate=s.onupdate,
            comment=s.comment,
            **kw,
        )
        # attach specs as attributes (no use of Column.info)
        self.colspec = spec
        self.io_spec = spec.io
        self.field_spec = spec.field
        self.storage_spec = s

    def __set_name__(self, owner, name: str) -> None:
        # Let SQLAlchemy do its normal setup first if available
        parent = getattr(super(), "__set_name__", None)
        if parent:
            parent(owner, name)
        # Bind spec to the class for later discovery/export
        colspecs = getattr(owner, "__autoapi_colspecs__", None)
        if colspecs is None:
            colspecs = {}
            setattr(owner, "__autoapi_colspecs__", colspecs)
        colspecs[name] = self.colspec


def acol(*, spec: ColumnSpec) -> SpecColumn:
    """Factory for class-body usage; returns a SpecColumn (descriptor)."""
    return SpecColumn(spec)
