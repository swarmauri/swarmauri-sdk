from __future__ import annotations

import datetime as dt

from ...specs import ColumnSpec, F, IO, S, acol
from ...types import (
    TZDateTime,
    Boolean,
    Integer,
    PgUUID,
    UUID,
    declarative_mixin,
    Mapped,
)

from .utils import tzutcnow, CRUD_IO, RO_IO


@declarative_mixin
class Created:
    created_at: Mapped[dt.datetime] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, default=tzutcnow, nullable=False),
            field=F(py_type=dt.datetime),
            io=RO_IO,
        )
    )


@declarative_mixin
class LastUsed:
    last_used_at: Mapped[dt.datetime | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, nullable=True, onupdate=tzutcnow),
            field=F(py_type=dt.datetime),
            io=IO(out_verbs=("read", "list", "create")),
        )
    )

    def touch(self) -> None:
        """Mark the object as used now."""
        self.last_used_at = tzutcnow()


@declarative_mixin
class Timestamped:
    created_at: Mapped[dt.datetime] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, default=tzutcnow, nullable=False),
            field=F(py_type=dt.datetime),
            io=RO_IO,
        )
    )
    updated_at: Mapped[dt.datetime] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=TZDateTime,
                default=tzutcnow,
                onupdate=tzutcnow,
                nullable=False,
            ),
            field=F(py_type=dt.datetime),
            io=RO_IO,
        )
    )


@declarative_mixin
class ActiveToggle:
    is_active: Mapped[bool] = acol(
        spec=ColumnSpec(
            storage=S(type_=Boolean, default=True, nullable=False),
            field=F(py_type=bool),
            io=CRUD_IO,
        )
    )


@declarative_mixin
class SoftDelete:
    deleted_at: Mapped[dt.datetime | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, nullable=True),
            field=F(py_type=dt.datetime),
            io=CRUD_IO,
        )
    )


@declarative_mixin
class Versioned:
    revision: Mapped[int] = acol(
        spec=ColumnSpec(
            storage=S(type_=Integer, default=1, nullable=False),
            field=F(py_type=int),
            io=CRUD_IO,
        )
    )
    prev_id: Mapped[UUID | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=PgUUID(as_uuid=True), nullable=True),
            field=F(py_type=UUID),
            io=CRUD_IO,
        )
    )


__all__ = [
    "Created",
    "LastUsed",
    "Timestamped",
    "ActiveToggle",
    "SoftDelete",
    "Versioned",
]
