"""Device code model."""

from __future__ import annotations

import datetime as dt
import uuid

from tigrbl_auth.deps import (
    Base,
    Timestamped,
    S,
    acol,
    ForeignKeySpec,
    Boolean,
    Integer,
    Mapped,
    PgUUID,
    String,
    TZDateTime,
    op_ctx,
    HTTPException,
    status,
)

from ..runtime_cfg import settings
from ..rfc.rfc8628 import (
    DEVICE_CODE_EXPIRES_IN,
    DEVICE_CODE_INTERVAL,
    DEVICE_VERIFICATION_URI,
)


class DeviceCode(Base, Timestamped):
    __tablename__ = "device_codes"
    __table_args__ = ({"schema": "authn"},)

    device_code: Mapped[str] = acol(storage=S(String(128), primary_key=True))
    user_code: Mapped[str] = acol(storage=S(String(32), nullable=False, index=True))
    client_id: Mapped[uuid.UUID] = acol(
        storage=S(
            PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="authn.clients.id"),
            nullable=False,
        )
    )
    expires_at: Mapped[dt.datetime] = acol(storage=S(TZDateTime, nullable=False))
    interval: Mapped[int] = acol(storage=S(Integer, nullable=False))
    authorized: Mapped[bool] = acol(storage=S(Boolean, nullable=False, default=False))
    user_id: Mapped[uuid.UUID | None] = acol(
        storage=S(
            PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="authn.users.id"),
            nullable=True,
            index=True,
        )
    )
    tenant_id: Mapped[uuid.UUID | None] = acol(
        storage=S(
            PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="authn.tenants.id"),
            nullable=True,
            index=True,
        )
    )

    @op_ctx(alias="device_authorization", target="create", arity="collection")
    async def device_authorization(cls, ctx):
        from datetime import datetime, timedelta, timezone
        from uuid import uuid4

        if not settings.enable_rfc8628:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, "device authorization disabled"
            )
        db = ctx.get("db")
        payload = ctx.get("payload") or {}
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "client_id required")
        device_code = uuid4().hex
        user_code = uuid4().hex[:8]
        verification_uri = DEVICE_VERIFICATION_URI
        verification_uri_complete = f"{verification_uri}?user_code={user_code}"
        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=DEVICE_CODE_EXPIRES_IN
        )
        await cls.handlers.create.core(
            {
                "db": db,
                "payload": {
                    "device_code": device_code,
                    "user_code": user_code,
                    "client_id": client_id,
                    "expires_at": expires_at,
                    "interval": DEVICE_CODE_INTERVAL,
                },
            }
        )
        return {
            "device_code": device_code,
            "user_code": user_code,
            "verification_uri": verification_uri,
            "verification_uri_complete": verification_uri_complete,
            "expires_in": DEVICE_CODE_EXPIRES_IN,
            "interval": DEVICE_CODE_INTERVAL,
        }


__all__ = ["DeviceCode"]
