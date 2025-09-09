from __future__ import annotations

from typing import Any, Callable, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import MappedColumn

from .column_spec import ColumnSpec
from .field_spec import FieldSpec as F
from .io_spec import IOSpec as IO
from .storage_spec import StorageSpec as S


class Column(ColumnSpec, MappedColumn):
    """SQLAlchemy column implementing a :class:`ColumnSpec`."""

    __slots__ = ()

    def __init__(
        self,
        *,
        spec: ColumnSpec | None = None,
        storage: S | None = None,
        field: F | None = None,
        io: IO | None = None,
        default_factory: Optional[Callable[[dict], Any]] = None,
        read_producer: Optional[Callable[[object, dict], Any]] = None,
        **kw: Any,
    ) -> None:
        if spec is not None and any(
            x is not None for x in (storage, field, io, default_factory, read_producer)
        ):
            raise ValueError("Provide either spec or individual components, not both.")
        if spec is None:
            spec = ColumnSpec(
                storage=storage,
                field=field,
                io=io,
                default_factory=default_factory,
                read_producer=read_producer,
            )
        else:
            storage = spec.storage
            field = spec.field
            io = spec.io
            default_factory = spec.default_factory
            read_producer = spec.read_producer

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
            MappedColumn.__init__(
                self,
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
        else:
            MappedColumn.__init__(self, **kw)

        self.storage = s
        self.field = field if field is not None else F()
        self.io = io if io is not None else IO()
        self.default_factory = default_factory
        self.read_producer = read_producer

    def __set_name__(self, owner, name: str) -> None:
        parent = getattr(super(), "__set_name__", None)
        if parent:
            parent(owner, name)
        colspecs = owner.__dict__.get("__tigrbl_colspecs__")
        if colspecs is None:
            base_specs = getattr(owner, "__tigrbl_colspecs__", {})
            colspecs = dict(base_specs)
            setattr(owner, "__tigrbl_colspecs__", colspecs)
        colspecs[name] = self
