"""ConnectedAccount – Stripe Connect account metadata."""

from __future__ import annotations

from enum import Enum

from tigrbl.table import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import Mapped, String, JSONB, Boolean, SAEnum, UniqueConstraint

from ._mixins.extref import StripeExtRef


class ConnectedType(Enum):
    STANDARD = "standard"
    EXPRESS = "express"
    CUSTOM = "custom"


class ConnectedAccount(Base, GUIDPk, Timestamped, StripeExtRef):
    __tablename__ = "connected_accounts"

    external_id: Mapped[str | None] = acol(
        storage=S(type_=String, nullable=True, unique=True, index=True),
        field=F(py_type=str | None),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
        name="stripe_account_id",
    )

    type: Mapped[ConnectedType] = acol(
        storage=S(type_=SAEnum, nullable=False),
        field=F(py_type=ConnectedType),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    payouts_enabled: Mapped[bool] = acol(
        storage=S(type_=Boolean, default=False, nullable=False),
        field=F(py_type=bool),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    charges_enabled: Mapped[bool] = acol(
        storage=S(type_=Boolean, default=False, nullable=False),
        field=F(py_type=bool),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    capabilities: Mapped[dict] = acol(
        storage=S(type_=JSONB, default=dict, nullable=False),
        field=F(py_type=dict),
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
        "stripe_account_id", name="uq_connected_accounts_stripe_account_id"
    )


__all__ = ["ConnectedAccount", "ConnectedType"]

for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__():
    return sorted(__all__)
