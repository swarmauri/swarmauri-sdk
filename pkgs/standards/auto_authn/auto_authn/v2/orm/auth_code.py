"""Authorization code model."""

from __future__ import annotations

from autoapi.v2 import Base
from autoapi.v2.mixins import Timestamped
from autoapi.v2.types import Column, ForeignKey, JSON, PgUUID, String, TZDateTime


class AuthCode(Base, Timestamped):
    __tablename__ = "auth_codes"
    __table_args__ = ({"schema": "authn"},)

    code = Column(String(128), primary_key=True)
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
    client_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("authn.clients.id"),
        nullable=False,
    )
    redirect_uri = Column(String(1000), nullable=False)
    code_challenge = Column(String, nullable=True)
    nonce = Column(String, nullable=True)
    scope = Column(String, nullable=True)
    expires_at = Column(TZDateTime, nullable=False)
    claims = Column(JSON, nullable=True)


__all__ = ["AuthCode"]
