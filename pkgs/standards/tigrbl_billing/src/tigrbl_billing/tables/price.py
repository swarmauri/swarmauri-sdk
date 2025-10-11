"""Price table – recurring/one-time prices with optional metering."""

from __future__ import annotations

from enum import Enum
from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped, ActiveToggle
from tigrbl.specs import F, IO, S, acol
from tigrbl.specs.storage_spec import ForeignKeySpec
from tigrbl.types import Integer, String, JSONB, SAEnum, Mapped
from tigrbl.orm.mixins.utils import _infer_schema


class BillingScheme(str, Enum):
    FLAT = "flat"
    TIERED = "tiered"
    PACKAGE = "package"
    GRADUATED = "graduated"


class RecurringInterval(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class UsageType(str, Enum):
    LICENSED = "licensed"
    METERED = "metered"


class AggregateUsage(str, Enum):
    SUM = "sum"
    LAST_DURING_PERIOD = "last_during_period"
    MAX = "max"
    LAST_EVER = "last_ever"


class TaxBehavior(str, Enum):
    INCLUSIVE = "inclusive"
    EXCLUSIVE = "exclusive"
    UNSPECIFIED = "unspecified"


class Price(Base, GUIDPk, Timestamped, ActiveToggle):
    __tablename__ = "billing_prices"

    # Stripe price id (e.g., "price_...")
    stripe_price_id: Mapped[str] = acol(
        storage=S(type_=String(64), unique=True, index=True, nullable=False),
        field=F(py_type=str, constraints={"max_length": 64}),
        io=IO(
            in_verbs=("create"),
            out_verbs=("read", "list"),
            mutable_verbs=("update"),
        ),
    )

    # FK -> Product
    product_id: Mapped[str] = acol(
        storage=S(
            type_=String(36),
            fk=ForeignKeySpec(
                # schema-qualified FK inferred from Product model's schema
                target=lambda cls: f"{_infer_schema(cls)}.billing_products.id"
            ),
            nullable=False,
            index=True,
        ),
        field=F(py_type=str),
        io=IO(
            in_verbs=("create", "update", "replace"),
            out_verbs=("read", "list"),
            mutable_verbs=("update", "replace"),
        ),
    )

    currency: Mapped[str] = acol(
        storage=S(type_=String(3), nullable=False, index=True),
        field=F(py_type=str, constraints={"min_length": 3, "max_length": 3}),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    billing_scheme: Mapped[BillingScheme] = acol(
        storage=S(type_=SAEnum(BillingScheme, name="billing_scheme"), nullable=False),
        field=F(py_type=BillingScheme),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    unit_amount: Mapped[int | None] = acol(
        storage=S(type_=Integer, nullable=True),
        field=F(py_type=int),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    recurring_interval: Mapped[RecurringInterval | None] = acol(
        storage=S(
            type_=SAEnum(RecurringInterval, name="recurring_interval"),
            nullable=True,
        ),
        field=F(py_type=RecurringInterval),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    recurring_count: Mapped[int | None] = acol(
        storage=S(type_=Integer, nullable=True),
        field=F(py_type=int),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    usage_type: Mapped[UsageType] = acol(
        storage=S(
            type_=SAEnum(UsageType, name="usage_type"), nullable=False, index=True
        ),
        field=F(py_type=UsageType),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    aggregate_usage: Mapped[AggregateUsage | None] = acol(
        storage=S(type_=SAEnum(AggregateUsage, name="aggregate_usage"), nullable=True),
        field=F(py_type=AggregateUsage),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    transform_quantity: Mapped[dict | None] = acol(
        storage=S(type_=JSONB, nullable=True),
        field=F(py_type=dict),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    tax_behavior: Mapped[TaxBehavior | None] = acol(
        storage=S(type_=SAEnum(TaxBehavior, name="tax_behavior"), nullable=True),
        field=F(py_type=TaxBehavior),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    nickname: Mapped[str | None] = acol(
        storage=S(type_=String(100), nullable=True, index=True),
        field=F(py_type=str, constraints={"max_length": 100}),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    metadata_: Mapped[dict | None] = acol(
        storage=S(type_=JSONB, nullable=True),
        field=F(py_type=dict),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
        name="metadata",
    )


__all__ = [
    "Price",
    "BillingScheme",
    "RecurringInterval",
    "UsageType",
    "AggregateUsage",
    "TaxBehavior",
]
