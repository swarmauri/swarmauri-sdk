"""CreditLedger – auditable ledger of credit debits/credits (no Upsertable)."""

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


class LedgerDirection(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"


class LedgerSource(str, Enum):
    TOP_OFF = "top_off"
    GRANT = "grant"
    USAGE = "usage"
    ADJUSTMENT = "adjustment"
    EXPIRATION = "expiration"
    REVERSAL = "reversal"


class CreditLedger(Base, GUIDPk, Timestamped):
    __tablename__ = "credit_ledger"

    customer_id: Mapped[UUID] = acol(
        storage=S(
            type_=PgUUID,
            nullable=False,
            fk=ForeignKeySpec("customers.id", ondelete="CASCADE"),
            index=True,
        ),
        field=F(py_type=str),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    currency: Mapped[str] = acol(
        storage=S(type_=String(8), nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    direction: Mapped[LedgerDirection] = acol(
        storage=S(type_=SAEnum(LedgerDirection), nullable=False),
        field=F(py_type=LedgerDirection),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    delta: Mapped[int] = acol(
        storage=S(type_=Integer, nullable=False),
        field=F(py_type=int),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    balance_id: Mapped[UUID | None] = acol(
        storage=S(
            type_=PgUUID,
            nullable=True,
            fk=ForeignKeySpec("customer_balances.id", ondelete="SET NULL"),
            index=True,
        ),
        field=F(py_type=str | None),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    grant_id: Mapped[UUID | None] = acol(
        storage=S(
            type_=PgUUID,
            nullable=True,
            fk=ForeignKeySpec("credit_grants.id", ondelete="SET NULL"),
            index=True,
        ),
        field=F(py_type=str | None),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    usage_event_id: Mapped[UUID | None] = acol(
        storage=S(
            type_=PgUUID,
            nullable=True,
            fk=ForeignKeySpec("usage_events.id", ondelete="SET NULL"),
            index=True,
        ),
        field=F(py_type=str | None),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    subject_ref: Mapped[str | None] = acol(
        storage=S(type_=String(256), nullable=True),
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


__all__ = ["CreditLedger", "LedgerDirection", "LedgerSource"]
