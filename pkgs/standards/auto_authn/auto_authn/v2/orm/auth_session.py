"""Authentication session model."""

from __future__ import annotations

import datetime as dt

from autoapi.v2 import Base
from autoapi.v2.mixins import Timestamped
from autoapi.v2.types import Column, ForeignKey, PgUUID, String, TZDateTime


class AuthSession(Base, Timestamped):
    __tablename__ = "sessions"
    __table_args__ = ({"schema": "authn"},)

    id = Column(String(64), primary_key=True)
    user_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("authn.users.id"),
        nullable=False,
        index=True,
    )
    tenant_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("authn.tenants.id"),
        nullable=False,
        index=True,
    )
    username = Column(String(120), nullable=False)
    auth_time = Column(
        TZDateTime, default=lambda: dt.datetime.now(dt.timezone.utc), nullable=False
    )


__all__ = ["AuthSession"]
