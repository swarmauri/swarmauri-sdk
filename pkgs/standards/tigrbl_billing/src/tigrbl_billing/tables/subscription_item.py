"""SubscriptionItem – per-price line of a subscription."""

from __future__ import annotations

from tigrbl.table import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped
from tigrbl.specs import F, IO, S, acol
from tigrbl.specs.storage_spec import ForeignKeySpec
from tigrbl.types import (
    Mapped,
    Integer,
    String,
    JSONB,
    UniqueConstraint,
    CheckConstraint,
    PgUUID,
    UUID,
)


class SubscriptionItem(Base, GUIDPk, Timestamped):
    __tablename__ = "subscription_items"

    subscription_id: Mapped[UUID] = acol(
        storage=S(
            type_=PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="subscriptions.id"),
            nullable=False,
            index=True,
        ),
        field=F(py_type=UUID),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    price_id: Mapped[UUID] = acol(
        storage=S(
            type_=PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="prices.id"),
            nullable=False,
            index=True,
        ),
        field=F(py_type=UUID),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    stripe_subscription_item_id: Mapped[str | None] = acol(
        storage=S(type_=String, nullable=True, unique=True, index=True),
        field=F(py_type=str | None),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    quantity: Mapped[int | None] = acol(
        storage=S(type_=Integer, nullable=True, default=1),
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
            "stripe_subscription_item_id", name="uq_si_stripe_subscription_item_id"
        ),
        CheckConstraint(
            "quantity IS NULL OR quantity >= 0", name="ck_si_quantity_nonneg"
        ),
    )


__all__ = ["SubscriptionItem"]

for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__():
    return sorted(__all__)
