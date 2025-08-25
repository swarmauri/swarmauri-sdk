"""Device code model."""

from __future__ import annotations

from autoapi.v2 import Base
from autoapi.v2.mixins import Timestamped
from autoapi.v2.types import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    PgUUID,
    String,
    TZDateTime,
)


class DeviceCode(Base, Timestamped):
    __tablename__ = "device_codes"
    __table_args__ = ({"schema": "authn"},)

    device_code = Column(String(128), primary_key=True)
    user_code = Column(String(32), nullable=False, index=True)
    client_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("authn.clients.id"),
        nullable=False,
    )
    expires_at = Column(TZDateTime, nullable=False)
    interval = Column(Integer, nullable=False)
    authorized = Column(Boolean, default=False, nullable=False)
    user_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("authn.users.id"),
        nullable=True,
        index=True,
    )
    tenant_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("authn.tenants.id"),
        nullable=True,
        index=True,
    )


__all__ = ["DeviceCode"]
