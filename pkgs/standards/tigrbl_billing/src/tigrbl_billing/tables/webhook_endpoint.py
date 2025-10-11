
"""WebhookEndpoint – local configuration for verifying Stripe webhooks."""
from __future__ import annotations

from tigrbl.table import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped
from tigrbl.specs import ColumnSpec, F, IO, S, acol
from tigrbl.types import (
    Mapped, String, JSONB, Boolean, UniqueConstraint)

class WebhookEndpoint(Base, GUIDPk, Timestamped):
    """Stores verification material and config for a webhook receiver.

    Upserts use (purpose, account) so you can maintain one endpoint per
    semantic purpose per connected account (or platform if account is NULL).
    """
    __tablename__ = "webhook_endpoints"


    purpose: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str, constraints={"examples": ["billing","connect"]}),
            io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")))
    )

    account: Mapped[str | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, nullable=True),
            field=F(py_type=str | None, constraints={"examples": ["acct_123", None]}),
            io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")))
    )

    signing_secret: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")))
    )

    active: Mapped[bool] = acol(
        spec=ColumnSpec(
            storage=S(type_=Boolean, default=True, nullable=False),
            field=F(py_type=bool),
            io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")))
    )

    config: Mapped[dict] = acol(
        spec=ColumnSpec(
            storage=S(type_=JSONB, default=dict, nullable=False),
            field=F(py_type=dict, constraints={"examples": [{"subscribed_events": ["*"], "notes": "default"}]}),
            io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")))
    )

    __table_args__ = (
        UniqueConstraint("purpose", "account", name="uq_webhook_endpoints_purpose_account"))

__all__ = ["WebhookEndpoint"]

def __dir__():
    return sorted(__all__)
