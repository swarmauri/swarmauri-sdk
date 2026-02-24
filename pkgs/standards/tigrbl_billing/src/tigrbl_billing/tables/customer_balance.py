"""CustomerBalance – per-customer currency balance (no Upsertable)."""

from __future__ import annotations
from enum import Enum
from tigrbl.table import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped, ActiveToggle
from tigrbl.specs import F, IO, S, acol
from tigrbl.specs.storage_spec import ForeignKeySpec
from tigrbl.types import (
    Mapped,
    String,
    Integer,
    JSONB,
    Boolean,
    SAEnum,
    UniqueConstraint,
    UUID,
    PgUUID,
)

from ._mixins.extref import StripeExtRef


class TopOffMode(str, Enum):
    MANUAL = "manual"
    AUTO = "auto"


class CustomerBalance(Base, GUIDPk, Timestamped, ActiveToggle, StripeExtRef):
    __tablename__ = "customer_balances"

    customer_id: Mapped[UUID] = acol(
        storage=S(
            type_=PgUUID,
            nullable=False,
            fk=ForeignKeySpec("customers.id", ondelete="CASCADE"),
            index=True,
        ),
        field=F(py_type=str),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    currency: Mapped[str] = acol(
        storage=S(type_=String(8), nullable=False, index=True),
        field=F(py_type=str),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    available_amount: Mapped[int] = acol(
        storage=S(type_=Integer, nullable=False, default=0),
        field=F(py_type=int),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    pending_amount: Mapped[int] = acol(
        storage=S(type_=Integer, nullable=False, default=0),
        field=F(py_type=int),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    hold_amount: Mapped[int] = acol(
        storage=S(type_=Integer, nullable=False, default=0),
        field=F(py_type=int),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    auto_top_off_enabled: Mapped[bool] = acol(
        storage=S(type_=Boolean, nullable=False, default=False),
        field=F(py_type=bool),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    top_off_mode: Mapped[TopOffMode] = acol(
        storage=S(type_=SAEnum(TopOffMode), nullable=False, default=TopOffMode.MANUAL),
        field=F(py_type=TopOffMode),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    top_off_threshold: Mapped[int | None] = acol(
        storage=S(type_=Integer, nullable=True),
        field=F(py_type=int),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    top_off_amount: Mapped[int | None] = acol(
        storage=S(type_=Integer, nullable=True),
        field=F(py_type=int),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    external_id: Mapped[str | None] = acol(
        storage=S(type_=String(128), nullable=True, index=True),
        field=F(py_type=str | None),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
        name="stripe_customer_id",
    )

    metadata_: Mapped[dict | None] = acol(
        storage=S(type_=JSONB, nullable=True),
        field=F(py_type=dict | None),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
        name="metadata",
    )

    __table_args__ = UniqueConstraint(
        "customer_id", "currency", name="uq_customer_balance_customer_currency"
    )


__all__ = ["CustomerBalance", "TopOffMode"]
