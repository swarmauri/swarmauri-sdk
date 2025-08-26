"""Device code model."""

from __future__ import annotations

import datetime as dt
import uuid

from autoapi.v3.tables import Base
from autoapi.v3.mixins import Timestamped
from autoapi.v3.specs import S, acol
from autoapi.v3.specs.storage_spec import ForeignKeySpec
from autoapi.v3.types import Boolean, Integer, PgUUID, String, TZDateTime
from autoapi.v3 import op_ctx


class DeviceCode(Base, Timestamped):
    __tablename__ = "device_codes"
    __table_args__ = ({"schema": "authn"},)

    device_code: str = acol(storage=S(String(128), primary_key=True))
    user_code: str = acol(storage=S(String(32), nullable=False, index=True))
    client_id: uuid.UUID = acol(
        storage=S(
            PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="authn.clients.id"),
            nullable=False,
        )
    )
    expires_at: dt.datetime = acol(storage=S(TZDateTime, nullable=False))
    interval: int = acol(storage=S(Integer, nullable=False))
    authorized: bool = acol(storage=S(Boolean, nullable=False, default=False))
    user_id: uuid.UUID | None = acol(
        storage=S(
            PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="authn.users.id"),
            nullable=True,
            index=True,
        )
    )
    tenant_id: uuid.UUID | None = acol(
        storage=S(
            PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="authn.tenants.id"),
            nullable=True,
            index=True,
        )
    )

    @op_ctx(alias="device_authorization", target="create", arity="collection")
    def device_authorization(cls, ctx):
        pass


__all__ = ["DeviceCode"]
