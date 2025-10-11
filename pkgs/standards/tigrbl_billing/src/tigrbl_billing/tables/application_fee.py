"""ApplicationFee – platform fees charged on top of payment for Connect."""

from __future__ import annotations

from tigrbl.table import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped
from tigrbl.specs import ColumnSpec, F, IO, S, acol
from tigrbl.specs.storage_spec import ForeignKeySpec
from tigrbl.types import (
    Mapped,
    String,
    Integer,
    JSONB,
    Boolean,
    UniqueConstraint,
    CheckConstraint,
    PgUUID,
    UUID,
)


class ApplicationFee(Base, GUIDPk, Timestamped):
    __tablename__ = "application_fees"

    stripe_application_fee_id: Mapped[str | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, nullable=True),
            field=F(py_type=str | None, constraints={"examples": ["fee_123"]}),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )
    )

    amount: Mapped[int] = acol(
        spec=ColumnSpec(
            storage=S(type_=Integer, nullable=False),
            field=F(py_type=int, constraints={"ge": 0}),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )
    )

    currency: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str, constraints={"max_length": 8}),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )
    )

    originating_payment_intent_id: Mapped[UUID | None] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target="payment_intents.id"),
                nullable=True,
            ),
            field=F(py_type=UUID | None),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )
    )

    connected_account_id: Mapped[UUID | None] = acol(
        spec=ColumnSpec(
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
    )

    refunded: Mapped[bool] = acol(
        spec=ColumnSpec(
            storage=S(type_=Boolean, default=False, nullable=False),
            field=F(py_type=bool),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )
    )

    metadata: Mapped[dict] = acol(
        spec=ColumnSpec(
            storage=S(type_=JSONB, default=dict, nullable=False),
            field=F(py_type=dict),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )
    )

    __table_args__ = (
        UniqueConstraint(
            "stripe_application_fee_id", name="uq_application_fees_stripe_id"
        ),
        CheckConstraint("amount >= 0", name="ck_application_fees_amount_nonneg"),
    )


__all__ = ["ApplicationFee"]


def __dir__():
    return sorted(__all__)
