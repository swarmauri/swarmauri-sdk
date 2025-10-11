"""UsageRollup – materialized usage by subscription item and period."""

from __future__ import annotations

import datetime as dt

from tigrbl.table import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped
from tigrbl.specs import ColumnSpec, F, IO, S, acol
from tigrbl.specs.storage_spec import ForeignKeySpec
from tigrbl.types import Mapped, Integer, TZDateTime, UniqueConstraint, PgUUID, UUID


class UsageRollup(Base, GUIDPk, Timestamped):
    __tablename__ = "usage_rollups"

    subscription_item_id: Mapped[UUID] = acol(
        spec=ColumnSpec(
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
    )

    period_start: Mapped[dt.datetime] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, nullable=False),
            field=F(py_type=dt.datetime),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )
    )

    period_end: Mapped[dt.datetime] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, nullable=False),
            field=F(py_type=dt.datetime),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )
    )

    quantity_sum: Mapped[int] = acol(
        spec=ColumnSpec(
            storage=S(type_=Integer, default=0, nullable=False),
            field=F(py_type=int),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )
    )

    last_event_ts: Mapped[dt.datetime | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, nullable=True),
            field=F(py_type=dt.datetime | None),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )
    )

    __table_args__ = UniqueConstraint(
        "subscription_item_id",
        "period_start",
        "period_end",
        name="uq_usage_rollup_window",
    )


__all__ = ["UsageRollup"]

for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__():
    return sorted(__all__)
