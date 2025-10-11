"""PaymentIntent – payment authorization, capture, and settlement state."""

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


class PaymentIntentStatus(Enum):
    REQUIRES_PAYMENT_METHOD = "requires_payment_method"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    REQUIRES_ACTION = "requires_action"
    PROCESSING = "processing"
    REQUIRES_CAPTURE = "requires_capture"
    CANCELED = "canceled"
    SUCCEEDED = "succeeded"


class CaptureMethod(Enum):
    AUTOMATIC = "automatic"
    MANUAL = "manual"


class PaymentIntent(Base, GUIDPk, Timestamped):
    __tablename__ = "payment_intents"

    stripe_payment_intent_id: Mapped[str | None] = acol(
        storage=S(type_=String, nullable=True),
        field=F(py_type=str | None, constraints={"examples": ["pi_123"]}),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    customer_id: Mapped[UUID | None] = acol(
        storage=S(
            type_=PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="customers.id"),
            nullable=True,
        ),
        field=F(py_type=UUID | None),
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

    amount: Mapped[int] = acol(
        storage=S(type_=Integer, nullable=False),
        field=F(py_type=int, constraints={"ge": 0}),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    status: Mapped[PaymentIntentStatus] = acol(
        storage=S(type_=SAEnum, nullable=False),
        field=F(py_type=PaymentIntentStatus),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    capture_method: Mapped[CaptureMethod] = acol(
        storage=S(type_=SAEnum, default=CaptureMethod.AUTOMATIC, nullable=False),
        field=F(py_type=CaptureMethod),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    payment_method_types: Mapped[dict] = acol(
        storage=S(type_=JSONB, default=list, nullable=False),
        field=F(py_type=dict),  # array of strings
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    connected_account_id: Mapped[UUID | None] = acol(
        storage=S(
            type_=PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="connected_accounts.id"),
            nullable=True,
        ),
        field=F(py_type=UUID | None),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    application_fee_amount: Mapped[int | None] = acol(
        storage=S(type_=Integer, nullable=True),
        field=F(py_type=int | None, constraints={"ge": 0}),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    transfer_data: Mapped[dict | None] = acol(
        storage=S(type_=JSONB, nullable=True),
        field=F(py_type=dict | None),
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
        UniqueConstraint(
            "stripe_payment_intent_id", name="uq_pi_stripe_payment_intent_id"
        ),
        CheckConstraint("amount >= 0", name="ck_pi_amount_nonneg"),
        CheckConstraint(
            "application_fee_amount IS NULL OR application_fee_amount >= 0",
            name="ck_pi_appfee_nonneg",
        ),
    )


__all__ = ["PaymentIntent", "PaymentIntentStatus", "CaptureMethod"]


def __dir__():
    return sorted(__all__)
