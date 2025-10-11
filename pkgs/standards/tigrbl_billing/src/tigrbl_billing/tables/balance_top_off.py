"""BalanceTopOff – records top-off attempts and results (no Upsertable)."""

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
    Integer,
    JSONB,
    SAEnum,
    UUID,
    PgUUID,
    TZDateTime,
)


class TopOffTrigger(str, Enum):
    MANUAL = "manual"
    AUTO = "auto"
    SYSTEM = "system"


class TopOffMethod(str, Enum):
    PAYMENT_INTENT = "payment_intent"
    EXTERNAL_TRANSFER = "external_transfer"
    GRANT = "grant"


class TopOffStatus(str, Enum):
    INITIATED = "initiated"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class BalanceTopOff(Base, GUIDPk, Timestamped):
    __tablename__ = "balance_top_offs"

    balance_id: Mapped[UUID] = acol(
        storage=S(
            type_=PgUUID,
            nullable=False,
            fk=ForeignKeySpec("customer_balances.id", ondelete="CASCADE"),
            index=True,
        ),
        field=F(py_type=str),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    amount: Mapped[int] = acol(
        storage=S(type_=Integer, nullable=False),
        field=F(py_type=int),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    currency: Mapped[str] = acol(
        storage=S(type_=String(8), nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    trigger: Mapped[TopOffTrigger] = acol(
        storage=S(type_=SAEnum(TopOffTrigger), nullable=False),
        field=F(py_type=TopOffTrigger),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    method: Mapped[TopOffMethod] = acol(
        storage=S(type_=SAEnum(TopOffMethod), nullable=False),
        field=F(py_type=TopOffMethod),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    status: Mapped[TopOffStatus] = acol(
        storage=S(
            type_=SAEnum(TopOffStatus),
            nullable=False,
            default=TopOffStatus.INITIATED,
        ),
        field=F(py_type=TopOffStatus),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    stripe_payment_intent_id: Mapped[str | None] = acol(
        storage=S(type_=String(128), nullable=True),
        field=F(py_type=str | None),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    processed_at: Mapped[dt.datetime | None] = acol(
        storage=S(type_=TZDateTime, nullable=True),
        field=F(py_type=dt.datetime | None),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    metadata: Mapped[dict | None] = acol(
        storage=S(type_=JSONB, nullable=True),
        field=F(py_type=dict | None),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )


__all__ = ["BalanceTopOff", "TopOffTrigger", "TopOffMethod", "TopOffStatus"]
