"""SeatAllocation – assignment of a seat to a subject (user/team/org)."""

from __future__ import annotations

import datetime as dt
from enum import Enum

from tigrbl.table import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped
from tigrbl.specs import F, IO, S, acol
from tigrbl.specs.storage_spec import ForeignKeySpec
from tigrbl.types import (
    Mapped,
    String,
    SAEnum,
    TZDateTime,
    UniqueConstraint,
    PgUUID,
    UUID,
)


class SeatState(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    RELEASED = "released"


class SeatAllocation(Base, GUIDPk, Timestamped):
    __tablename__ = "seat_allocations"

    subscription_item_id: Mapped[UUID] = acol(
        storage=S(
            type_=PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="subscription_items.id"),
            nullable=False,
            index=True,
        ),
        field=F(py_type=UUID),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    subject_ref: Mapped[str] = acol(
        storage=S(type_=String, nullable=False, index=True),
        field=F(py_type=str, constraints={"examples": ["user:123", "team:alpha"]}),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    role: Mapped[str | None] = acol(
        storage=S(type_=String, nullable=True),
        field=F(py_type=str | None),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    state: Mapped[SeatState] = acol(
        storage=S(type_=SAEnum, default=SeatState.ACTIVE, nullable=False),
        field=F(py_type=SeatState),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    assigned_at: Mapped[dt.datetime] = acol(
        storage=S(type_=TZDateTime, nullable=False),
        field=F(py_type=dt.datetime),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    released_at: Mapped[dt.datetime | None] = acol(
        storage=S(type_=TZDateTime, nullable=True),
        field=F(py_type=dt.datetime | None),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    __table_args__ = UniqueConstraint(
        "subscription_item_id", "subject_ref", name="uq_seat_unique_assignment"
    )


__all__ = ["SeatAllocation", "SeatState"]

for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__():
    return sorted(__all__)
