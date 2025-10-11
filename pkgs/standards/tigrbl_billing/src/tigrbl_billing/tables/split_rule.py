"""SplitRule – deterministic mapping for Connect split semantics."""

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


class SplitMode(Enum):
    DIRECT = "direct"  # direct charges on connected account
    DESTINATION = "destination"  # destination charges (transfer_data.destination)
    SEPARATE = "separate"  # separate charges & transfers


class SplitRule(Base, GUIDPk, Timestamped):
    __tablename__ = "split_rules"

    key: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str, constraints={"max_length": 120}),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    mode: Mapped[SplitMode] = acol(
        storage=S(type_=SAEnum, default=SplitMode.DESTINATION, nullable=False),
        field=F(py_type=SplitMode),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    application_fee_bps: Mapped[int | None] = acol(
        storage=S(type_=Integer, nullable=True),
        field=F(
            py_type=int | None, constraints={"ge": 0, "le": 10000}
        ),  # basis points (0..10000)
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    fixed_application_fee_amount: Mapped[int | None] = acol(
        storage=S(type_=Integer, nullable=True),
        field=F(py_type=int | None, constraints={"ge": 0}),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    transfer_dest_account_id: Mapped[UUID | None] = acol(
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

    metadata: Mapped[dict] = acol(
        storage=S(type_=JSONB, default=dict, nullable=False),
        field=F(py_type=dict),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    __table_args__ = (
        UniqueConstraint("key", name="uq_split_rules_key"),
        CheckConstraint(
            "application_fee_bps IS NULL OR (application_fee_bps >= 0 AND application_fee_bps <= 10000)",
            name="ck_split_rules_bps_range",
        ),
        CheckConstraint(
            "fixed_application_fee_amount IS NULL OR fixed_application_fee_amount >= 0",
            name="ck_split_rules_fixed_nonneg",
        ),
    )


__all__ = ["SplitRule", "SplitMode"]


def __dir__():
    return sorted(__all__)
