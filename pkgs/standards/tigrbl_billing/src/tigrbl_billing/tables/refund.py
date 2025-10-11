"""Refund – refunds tied to a PaymentIntent (or Charge) with status."""

from __future__ import annotations

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
    UniqueConstraint,
    CheckConstraint,
    PgUUID,
    UUID,
)

from ._extref import StripeExtRef, stripe_external_id_spec


class RefundStatus(Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"


class Refund(Base, GUIDPk, Timestamped, StripeExtRef):
    __tablename__ = "refunds"

    stripe_refund_id: Mapped[str | None]
    __extref_external_id_attr__ = "stripe_refund_id"
    __extref_external_id_column__ = "stripe_refund_id"
    __extref_external_id_spec__ = stripe_external_id_spec(
        nullable=True,
        in_verbs=("create", "update", "replace", "merge"),
        out_verbs=("read", "list"),
        mutable_verbs=("update", "replace", "merge"),
    )

    payment_intent_id: Mapped[UUID] = acol(
        storage=S(
            type_=PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="payment_intents.id"),
            nullable=False,
        ),
        field=F(py_type=UUID),
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

    status: Mapped[RefundStatus] = acol(
        storage=S(type_=SAEnum, nullable=False),
        field=F(py_type=RefundStatus),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    reason: Mapped[str | None] = acol(
        storage=S(type_=String, nullable=True),
        field=F(py_type=str | None),
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
        UniqueConstraint("stripe_refund_id", name="uq_refunds_stripe_refund_id"),
        CheckConstraint("amount >= 0", name="ck_refunds_amount_nonneg"),
    )


__all__ = ["Refund", "RefundStatus"]


def __dir__():
    return sorted(__all__)
