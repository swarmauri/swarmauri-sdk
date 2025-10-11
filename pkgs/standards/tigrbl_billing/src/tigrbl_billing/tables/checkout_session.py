"""CheckoutSession – Stripe Checkout session lifecyle and result binding."""

from __future__ import annotations

from enum import Enum

from tigrbl.table import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped
from tigrbl.specs import F, IO, S, acol
from tigrbl.specs.storage_spec import ForeignKeySpec
from tigrbl.types import (
    Mapped,
    String,
    JSONB,
    SAEnum,
    UniqueConstraint,
    PgUUID,
    UUID,
    TZDateTime,
)


class CheckoutMode(Enum):
    PAYMENT = "payment"
    SETUP = "setup"
    SUBSCRIPTION = "subscription"


class CheckoutStatus(Enum):
    OPEN = "open"
    COMPLETE = "complete"
    EXPIRED = "expired"


class CheckoutSession(Base, GUIDPk, Timestamped):
    __tablename__ = "checkout_sessions"

    stripe_checkout_session_id: Mapped[str | None] = acol(
        storage=S(type_=String, nullable=True),
        field=F(py_type=str | None, constraints={"examples": ["cs_test_123"]}),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    mode: Mapped[CheckoutMode] = acol(
        storage=S(type_=SAEnum, nullable=False),
        field=F(py_type=CheckoutMode),
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

    status: Mapped[CheckoutStatus] = acol(
        storage=S(type_=SAEnum, nullable=False),
        field=F(py_type=CheckoutStatus),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    success_url: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    cancel_url: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    line_items: Mapped[dict] = acol(
        storage=S(type_=JSONB, default=list, nullable=False),
        field=F(py_type=dict),  # stored as JSON array/object
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

    completed_at: Mapped[object | None] = acol(
        storage=S(type_=TZDateTime, nullable=True),
        field=F(py_type=object | None),
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

    __table_args__ = UniqueConstraint(
        "stripe_checkout_session_id", name="uq_chk_sessions_stripe_id"
    )


__all__ = ["CheckoutSession", "CheckoutMode", "CheckoutStatus"]


def __dir__():
    return sorted(__all__)
