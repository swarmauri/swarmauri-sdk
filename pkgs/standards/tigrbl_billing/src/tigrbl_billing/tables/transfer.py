"""Transfer – Stripe Connect fund movements to destination accounts."""

from __future__ import annotations

from tigrbl.table import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped
from tigrbl.specs import F, IO, S, acol
from tigrbl.specs.storage_spec import ForeignKeySpec
from tigrbl.types import (
    Mapped,
    String,
    Integer,
    JSONB,
    Boolean,
    UniqueConstraint,
    CheckConstraint,
    PgUUID,
    UUID,
)

from ._mixins.extref import StripeExtRef


class Transfer(Base, GUIDPk, Timestamped, StripeExtRef):
    __tablename__ = "transfers"

    external_id: Mapped[str | None] = acol(
        storage=S(type_=String, nullable=True),
        field=F(py_type=str | None, constraints={"examples": ["tr_123"]}),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
        name="stripe_transfer_id",
    )

    payment_intent_id: Mapped[UUID | None] = acol(
        storage=S(
            type_=PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="payment_intents.id"),
            nullable=True,
        ),
        field=F(py_type=UUID | None),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    amount: Mapped[int] = acol(
        storage=S(type_=Integer, nullable=False),
        field=F(py_type=int, constraints={"ge": 0}),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    currency: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str, constraints={"max_length": 8}),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    destination_account_id: Mapped[UUID] = acol(
        storage=S(
            type_=PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="connected_accounts.id"),
            nullable=False,
        ),
        field=F(py_type=UUID),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    reversed: Mapped[bool] = acol(
        storage=S(type_=Boolean, default=False, nullable=False),
        field=F(py_type=bool),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    metadata_: Mapped[dict] = acol(
        storage=S(type_=JSONB, default=dict, nullable=False),
        field=F(py_type=dict),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
        name="metadata",
    )

    __table_args__ = (
        UniqueConstraint("stripe_transfer_id", name="uq_transfers_stripe_transfer_id"),
        CheckConstraint("amount >= 0", name="ck_transfers_amount_nonneg"),
    )


__all__ = ["Transfer"]


def __dir__():
    return sorted(__all__)
