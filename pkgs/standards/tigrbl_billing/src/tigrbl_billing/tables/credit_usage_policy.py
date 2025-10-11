"""CreditUsagePolicy – maps usage features to credit cost (no Upsertable)."""

from __future__ import annotations
from tigrbl.table import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped, ActiveToggle
from tigrbl.specs import ColumnSpec, F, IO, S, acol
from tigrbl.types import Mapped, String, Integer, JSONB, UniqueConstraint


class CreditUsagePolicy(Base, GUIDPk, Timestamped, ActiveToggle):
    __tablename__ = "credit_usage_policies"

    feature_key: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String(128), nullable=False, index=True),
            field=F(py_type=str),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )
    )

    credits_per_unit: Mapped[int] = acol(
        spec=ColumnSpec(
            storage=S(type_=Integer, nullable=False),
            field=F(py_type=int),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )
    )

    min_granularity: Mapped[int | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=Integer, nullable=True),
            field=F(py_type=int | None),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )
    )

    metadata: Mapped[dict | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=JSONB, nullable=True),
            field=F(py_type=dict | None),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )
    )

    __table_args__ = UniqueConstraint(
        "feature_key", name="uq_credit_usage_policies_feature_key"
    )


__all__ = ["CreditUsagePolicy"]
