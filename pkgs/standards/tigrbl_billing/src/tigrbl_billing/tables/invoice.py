"""Invoice – Stripe invoice snapshot and collections state."""

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
    TZDateTime,
)


class InvoiceStatus(Enum):
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    UNCOLLECTIBLE = "uncollectible"
    VOID = "void"


class CollectionMethod(Enum):
    CHARGE_AUTOMATICALLY = "charge_automatically"
    SEND_INVOICE = "send_invoice"


class Invoice(Base, GUIDPk, Timestamped):
    __tablename__ = "invoices"

    stripe_invoice_id: Mapped[str | None] = acol(
        storage=S(type_=String, nullable=True),
        field=F(py_type=str | None, constraints={"examples": ["in_123"]}),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    customer_id: Mapped[UUID] = acol(
        storage=S(
            type_=PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="customers.id"),
            nullable=False,
        ),
        field=F(py_type=UUID),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    subscription_id: Mapped[UUID | None] = acol(
        storage=S(
            type_=PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="subscriptions.id"),
            nullable=True,
        ),
        field=F(py_type=UUID | None),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    status: Mapped[InvoiceStatus] = acol(
        storage=S(type_=SAEnum, nullable=False),
        field=F(py_type=InvoiceStatus),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    number: Mapped[str | None] = acol(
        storage=S(type_=String, nullable=True),
        field=F(py_type=str | None),
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

    total: Mapped[int] = acol(
        storage=S(type_=Integer, nullable=False),
        field=F(py_type=int, constraints={"ge": 0}),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    amount_due: Mapped[int] = acol(
        storage=S(type_=Integer, nullable=False),
        field=F(py_type=int, constraints={"ge": 0}),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    amount_paid: Mapped[int] = acol(
        storage=S(type_=Integer, nullable=False),
        field=F(py_type=int, constraints={"ge": 0}),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    amount_remaining: Mapped[int] = acol(
        storage=S(type_=Integer, nullable=False),
        field=F(py_type=int, constraints={"ge": 0}),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    due_date: Mapped[object | None] = acol(
        storage=S(type_=TZDateTime, nullable=True),
        field=F(py_type=object | None),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    hosted_invoice_url: Mapped[str | None] = acol(
        storage=S(type_=String, nullable=True),
        field=F(py_type=str | None),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    collection_method: Mapped[CollectionMethod] = acol(
        storage=S(type_=SAEnum, nullable=False),
        field=F(py_type=CollectionMethod),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    metadata: Mapped[dict] = acol(
        storage=S(type_=JSONB, default=dict, nullable=False),
        field=F(py_type=dict),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    __table_args__ = (
        UniqueConstraint("stripe_invoice_id", name="uq_invoices_stripe_invoice_id"),
        CheckConstraint(
            "total >= 0 AND amount_due >= 0 AND amount_paid >= 0 AND amount_remaining >= 0",
            name="ck_invoices_amounts_nonneg",
        ),
    )


__all__ = ["Invoice", "InvoiceStatus", "CollectionMethod"]


def __dir__():
    return sorted(__all__)
