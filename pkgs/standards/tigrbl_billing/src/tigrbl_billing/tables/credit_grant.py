"""CreditGrant – promotional/service credit allocations (no Upsertable)."""

from __future__ import annotations
import datetime as dt
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
    SAEnum,
    UUID,
    PgUUID,
    TZDateTime,
)


class GrantStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


class GrantType(str, Enum):
    PROMO = "promo"
    SERVICE = "service"
    GOODWILL = "goodwill"
    REFUND = "refund"
    MANUAL = "manual"


class CreditGrant(Base, GUIDPk, Timestamped, ActiveToggle):
    __tablename__ = "credit_grants"

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
        storage=S(type_=String(8), nullable=False),
        field=F(py_type=str),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    total_amount: Mapped[int] = acol(
        storage=S(type_=Integer, nullable=False),
        field=F(py_type=int),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    remaining_amount: Mapped[int] = acol(
        storage=S(type_=Integer, nullable=False, default=0),
        field=F(py_type=int),
        io=IO(in_verbs=("update", "replace", "merge"), out_verbs=("read", "list")),
    )

    grant_type: Mapped[GrantType] = acol(
        storage=S(type_=SAEnum(GrantType), nullable=False),
        field=F(py_type=GrantType),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    starts_at: Mapped[dt.datetime | None] = acol(
        storage=S(type_=TZDateTime, nullable=True),
        field=F(py_type=dt.datetime | None),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    expires_at: Mapped[dt.datetime | None] = acol(
        storage=S(type_=TZDateTime, nullable=True),
        field=F(py_type=dt.datetime | None),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    status: Mapped[GrantStatus] = acol(
        storage=S(
            type_=SAEnum(GrantStatus), nullable=False, default=GrantStatus.ACTIVE
        ),
        field=F(py_type=GrantStatus),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
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


__all__ = ["CreditGrant", "GrantStatus", "GrantType"]
