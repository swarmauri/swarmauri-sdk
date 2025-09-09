from __future__ import annotations

import datetime as dt

from ...specs import ColumnSpec, F, S, acol
from ...specs.storage_spec import ForeignKeySpec
from ...types import PgUUID, TZDateTime, UUID, declarative_mixin, Mapped

from .utils import CRUD_IO


@declarative_mixin
class RowLock:
    lock_token: Mapped[UUID | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=PgUUID(as_uuid=True), nullable=True),
            field=F(py_type=UUID),
            io=CRUD_IO,
        )
    )
    locked_at: Mapped[dt.datetime | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, nullable=True),
            field=F(py_type=dt.datetime),
            io=CRUD_IO,
        )
    )


@declarative_mixin
class SoftLock:
    locked_by: Mapped[UUID | None] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target="users.id"),
            ),
            field=F(py_type=UUID),
            io=CRUD_IO,
        )
    )
    locked_at: Mapped[dt.datetime | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime),
            field=F(py_type=dt.datetime),
            io=CRUD_IO,
        )
    )


__all__ = ["RowLock", "SoftLock"]
