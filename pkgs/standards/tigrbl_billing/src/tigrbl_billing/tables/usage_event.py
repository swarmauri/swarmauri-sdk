"""UsageEvent – raw usage signals for metered features."""
from __future__ import annotations

import datetime as dt
from enum import Enum

from tigrbl.table import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped
from tigrbl.specs import ColumnSpec, F, IO, S, acol
from tigrbl.specs.storage_spec import ForeignKeySpec
from tigrbl.types import Mapped, Integer, String, JSONB, SAEnum, UniqueConstraint, TZDateTime, PgUUID, UUID

class UsageSource(Enum):
    API = "api"
    IMPORT = "import"
    JOB = "job"
    HOOK = "hook"

class UsageEvent(Base, GUIDPk, Timestamped):
    __tablename__ = "usage_events"

    subscription_item_id: Mapped[UUID] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target="subscription_items.id"),
                nullable=False,
                index=True),
            field=F(py_type=UUID),
            io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")))
    )

    feature_id: Mapped[UUID | None] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target="features.id"),
                nullable=True,
                index=True),
            field=F(py_type=UUID | None),
            io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")))
    )

    quantity: Mapped[int] = acol(
        spec=ColumnSpec(
            storage=S(type_=Integer, nullable=False),
            field=F(py_type=int),
            io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")))
    )

    event_ts: Mapped[dt.datetime] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, nullable=False),
            field=F(py_type=dt.datetime),
            io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")))
    )

    idempotency_key: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, nullable=False, unique=True, index=True),
            field=F(py_type=str),
            io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")))
    )

    source: Mapped[UsageSource] = acol(
        spec=ColumnSpec(
            storage=S(type_=SAEnum, nullable=False),
            field=F(py_type=UsageSource),
            io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")))
    )

    metadata: Mapped[dict] = acol(
        spec=ColumnSpec(
            storage=S(type_=JSONB, default=dict, nullable=False),
            field=F(py_type=dict),
            io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")))
    )

    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_usage_events_idempotency"))

__all__ = ["UsageEvent", "UsageSource"]

for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]

def __dir__():
    return sorted(__all__)
