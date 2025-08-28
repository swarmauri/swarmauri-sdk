from __future__ import annotations

from typing import Any, Callable, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import MappedColumn

from .field_spec import FieldSpec as F
from .io_spec import IOSpec as IO
from .storage_spec import StorageSpec as S


class ColumnSpec(MappedColumn):
    """SQLAlchemy column carrying AutoAPI specs as attributes."""

    __slots__ = ("storage", "field", "io", "default_factory", "read_producer")

    def __init__(
        self,
        *,
        storage: S | None,
        field: F | None = None,
        io: IO | None = None,
        default_factory: Optional[Callable[[dict], Any]] = None,
        read_producer: Optional[Callable[[object, dict], Any]] = None,
        **kw: Any,
    ) -> None:
        s = storage
        if s is not None:
            args: list[Any] = [s.type_]
            fk = getattr(s, "fk", None)
            if fk is not None:
                args.append(
                    ForeignKey(
                        fk.target,
                        ondelete=fk.on_delete,
                        onupdate=fk.on_update,
                        deferrable=fk.deferrable,
                        initially="DEFERRED" if fk.initially_deferred else "IMMEDIATE",
                        match=fk.match,
                    )
                )
            super().__init__(
                *args,
                primary_key=s.primary_key,
                nullable=s.nullable,
                unique=s.unique,
                index=s.index,
                default=s.default,
                autoincrement=s.autoincrement,
                server_default=s.server_default,
                onupdate=s.onupdate,
                comment=s.comment,
                **kw,
            )
        else:  # virtual column, no storage
            super().__init__(**kw)
        self.storage = s
        self.field = field if field is not None else F()
        self.io = io if io is not None else IO()
        self.default_factory = default_factory
        self.read_producer = read_producer

    def __set_name__(self, owner, name: str) -> None:
        parent = getattr(super(), "__set_name__", None)
        if parent:
            parent(owner, name)
        colspecs = getattr(owner, "__autoapi_colspecs__", None)
        if colspecs is None:
            colspecs = {}
            setattr(owner, "__autoapi_colspecs__", colspecs)
        colspecs[name] = self
