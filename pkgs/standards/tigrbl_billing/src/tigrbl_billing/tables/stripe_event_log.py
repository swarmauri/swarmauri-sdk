"""StripeEventLog – signed webhook events (audit & idempotency)."""

from __future__ import annotations

from enum import Enum

from tigrbl.table import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import Mapped, String, JSONB, SAEnum, UniqueConstraint, TZDateTime

from ._mixins.extref import StripeExtRef


class EventProcessStatus(Enum):
    RECEIVED = "received"
    PROCESSED = "processed"
    FAILED = "failed"


class StripeEventLog(Base, GUIDPk, Timestamped, StripeExtRef):
    """Persist every Stripe webhook event once for audit + idempotent handling.

    Notes:
      • ``stripe_event_id`` is UNIQUE for exactly-once semantics
      • ``event_type`` mirrors Stripe's event.type (e.g., 'invoice.finalized')
      • ``event_created_ts`` stores the Stripe event's own timestamp (not our received time)
      • ``account`` holds a Connect account id when sent from a connected account
      • ``payload`` contains the full, verified JSON payload (for audit & repair)
    """

    __tablename__ = "stripe_event_logs"

    external_id: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
        name="stripe_event_id",
    )

    event_type: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    api_version: Mapped[str | None] = acol(
        storage=S(type_=String, nullable=True),
        field=F(py_type=str | None),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    event_created_ts: Mapped[object | None] = acol(
        storage=S(type_=TZDateTime, nullable=True),
        field=F(py_type=object | None),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    account: Mapped[str | None] = acol(
        storage=S(type_=String, nullable=True),
        field=F(py_type=str | None, constraints={"examples": ["acct_123"]}),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    payload: Mapped[dict] = acol(
        storage=S(type_=JSONB, nullable=False, default=dict),
        field=F(py_type=dict),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    status: Mapped[EventProcessStatus] = acol(
        storage=S(type_=SAEnum, default=EventProcessStatus.RECEIVED, nullable=False),
        field=F(py_type=EventProcessStatus),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    processed_at: Mapped[object | None] = acol(
        storage=S(type_=TZDateTime, nullable=True),
        field=F(py_type=object | None),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    error_message: Mapped[str | None] = acol(
        storage=S(type_=String, nullable=True),
        field=F(py_type=str | None),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    stripe_request_id: Mapped[str | None] = acol(
        storage=S(type_=String, nullable=True),
        field=F(py_type=str | None),
        io=IO(
            in_verbs=("create", "update", "replace", "merge"),
            out_verbs=("read", "list"),
        ),
    )

    __table_args__ = UniqueConstraint(
        "stripe_event_id", name="uq_stripe_event_logs_event_id"
    )


__all__ = ["StripeEventLog", "EventProcessStatus"]


def __dir__():
    return sorted(__all__)
