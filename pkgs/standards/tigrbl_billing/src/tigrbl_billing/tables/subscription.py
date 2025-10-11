"""Subscription model – lifecycle & periods."""

from __future__ import annotations

import datetime as dt
from enum import Enum

from tigrbl.table import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped
from tigrbl.specs import F, IO, S, acol
from tigrbl.specs.storage_spec import ForeignKeySpec
from tigrbl.types import (
    Mapped,
    Integer,
    JSONB,
    Boolean,
    SAEnum,
    UniqueConstraint,
    CheckConstraint,
    TZDateTime,
    PgUUID,
    UUID,
)

from ._extref import StripeExtRef, stripe_external_id_spec


class SubscriptionStatus(Enum):
    INCOMPLETE = "incomplete"
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"


class CollectionMethod(Enum):
    CHARGE_AUTOMATICALLY = "charge_automatically"
    SEND_INVOICE = "send_invoice"


class Subscription(Base, GUIDPk, Timestamped, StripeExtRef):
    __tablename__ = "subscriptions"

    stripe_subscription_id: Mapped[str | None]
    __extref_external_id_attr__ = "stripe_subscription_id"
    __extref_external_id_column__ = "stripe_subscription_id"
    __extref_external_id_spec__ = stripe_external_id_spec(
        nullable=True,
        in_verbs=("create", "update", "replace", "merge"),
        out_verbs=("read", "list"),
        mutable_verbs=("update", "replace", "merge"),
    )

    customer_id: Mapped[UUID] = acol(
        storage=S(
            type_=PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="customers.id"),
            nullable=False,
            index=True,
        ),
        field=F(py_type=UUID),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    status: Mapped[SubscriptionStatus] = acol(
        storage=S(type_=SAEnum, default=SubscriptionStatus.INCOMPLETE, nullable=False),
        field=F(py_type=SubscriptionStatus),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    start_date: Mapped[dt.datetime] = acol(
        storage=S(type_=TZDateTime, nullable=False),
        field=F(py_type=dt.datetime),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    cancel_at_period_end: Mapped[bool] = acol(
        storage=S(type_=Boolean, default=False, nullable=False),
        field=F(py_type=bool),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    current_period_start: Mapped[dt.datetime] = acol(
        storage=S(type_=TZDateTime, nullable=False),
        field=F(py_type=dt.datetime),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    current_period_end: Mapped[dt.datetime] = acol(
        storage=S(type_=TZDateTime, nullable=False),
        field=F(py_type=dt.datetime),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    trial_end: Mapped[dt.datetime | None] = acol(
        storage=S(type_=TZDateTime, nullable=True),
        field=F(py_type=dt.datetime | None),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    collection_method: Mapped[CollectionMethod] = acol(
        storage=S(
            type_=SAEnum,
            default=CollectionMethod.CHARGE_AUTOMATICALLY,
            nullable=False,
        ),
        field=F(py_type=CollectionMethod),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    days_until_due: Mapped[int | None] = acol(
        storage=S(type_=Integer, nullable=True),
        field=F(py_type=int | None),
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
            "stripe_subscription_id", name="uq_subs_stripe_subscription_id"
        ),
        CheckConstraint(
            "current_period_end > current_period_start", name="ck_subs_period_valid"
        ),
    )


__all__ = ["Subscription", "SubscriptionStatus", "CollectionMethod"]

for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__():
    return sorted(__all__)
