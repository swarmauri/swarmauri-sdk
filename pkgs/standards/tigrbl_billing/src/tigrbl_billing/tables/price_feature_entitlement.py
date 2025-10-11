"""PriceFeatureEntitlement – per-price feature limits/overages."""

from __future__ import annotations

from enum import Enum
from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped
from tigrbl.specs import F, IO, S, acol
from tigrbl.specs.storage_spec import ForeignKeySpec
from tigrbl.types import Integer, SAEnum, UniqueConstraint, Mapped
from tigrbl.orm.mixins.utils import _infer_schema


class EntitlementPeriod(str, Enum):
    DAY = "day"
    MONTH = "month"
    YEAR = "year"


class MeteringWindow(str, Enum):
    CALENDAR = "calendar"
    ROLLING = "rolling"


class PriceFeatureEntitlement(Base, GUIDPk, Timestamped):
    __tablename__ = "billing_price_feature_entitlements"

    price_id: Mapped[str] = acol(
        storage=S(
            type_=str,
            fk=ForeignKeySpec(
                target=lambda cls: f"{_infer_schema(cls)}.billing_prices.id"
            ),
            nullable=False,
            index=True,
        ),
        field=F(py_type=str),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    feature_id: Mapped[str] = acol(
        storage=S(
            type_=str,
            fk=ForeignKeySpec(
                target=lambda cls: f"{_infer_schema(cls)}.billing_features.id"
            ),
            nullable=False,
            index=True,
        ),
        field=F(py_type=str),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    limit_per_period: Mapped[int | None] = acol(
        storage=S(type_=Integer, nullable=True),
        field=F(py_type=int),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    overage_unit_amount: Mapped[int | None] = acol(
        storage=S(type_=Integer, nullable=True),
        field=F(py_type=int),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    period: Mapped[EntitlementPeriod | None] = acol(
        storage=S(
            type_=SAEnum(EntitlementPeriod, name="entitlement_period"),
            nullable=True,
        ),
        field=F(py_type=EntitlementPeriod),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    metering_window: Mapped[MeteringWindow | None] = acol(
        storage=S(type_=SAEnum(MeteringWindow, name="metering_window"), nullable=True),
        field=F(py_type=MeteringWindow),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    __table_args__ = UniqueConstraint("price_id", "feature_id", name="uq_price_feature")


__all__ = ["PriceFeatureEntitlement", "EntitlementPeriod", "MeteringWindow"]
