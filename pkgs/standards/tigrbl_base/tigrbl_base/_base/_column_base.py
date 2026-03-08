from __future__ import annotations

from typing import Any, Callable, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import MappedColumn

from tigrbl_core._spec.column_spec import ColumnSpec
from tigrbl_core._spec.field_spec import FieldSpec as F
from tigrbl_core._spec.io_spec import IOSpec as IO
from tigrbl_core._spec.serde import SerdeMixin
from tigrbl_core._spec.storage_spec import StorageSpec as S


class ColumnBase(SerdeMixin, ColumnSpec, MappedColumn):
    """Base SQLAlchemy column implementing the core ``ColumnSpec`` contract."""

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
            storage = storage
            field = field if field is not None else F()
            io = io if io is not None else IO()
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

    @property
    def storage(self) -> S | None:
        return self.__dict__["storage"]

    @storage.setter
    def storage(self, value: S | None) -> None:
        self.__dict__["storage"] = value

    @property
    def field(self) -> F:
        return self.__dict__["field"]

    @field.setter
    def field(self, value: F) -> None:
        self.__dict__["field"] = value

    @property
    def io(self) -> IO:
        return self.__dict__["io"]

    @io.setter
    def io(self, value: IO) -> None:
        self.__dict__["io"] = value

    @property
    def default_factory(self) -> Optional[Callable[[dict], Any]]:
        return self.__dict__["default_factory"]

    @default_factory.setter
    def default_factory(self, value: Optional[Callable[[dict], Any]]) -> None:
        self.__dict__["default_factory"] = value

    @property
    def read_producer(self) -> Optional[Callable[[object, dict], Any]]:
        return self.__dict__["read_producer"]

    @read_producer.setter
    def read_producer(self, value: Optional[Callable[[object, dict], Any]]) -> None:
        self.__dict__["read_producer"] = value

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


__all__ = ["ColumnBase"]
