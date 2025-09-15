"""Pushed authorization request model."""

from __future__ import annotations

import datetime as dt

from ..deps import (
    Base,
    Timestamped,
    S,
    acol,
    JSON,
    Mapped,
    String,
    TZDateTime,
    op_ctx,
    HTTPException,
    status,
)

from ..runtime_cfg import settings
from ..rfc.rfc9126 import DEFAULT_PAR_EXPIRY


class PushedAuthorizationRequest(Base, Timestamped):
    __tablename__ = "par_requests"
    __table_args__ = ({"schema": "authn"},)

    request_uri: Mapped[str] = acol(storage=S(String(255), primary_key=True))
    params: Mapped[dict] = acol(storage=S(JSON, nullable=False))
    expires_at: Mapped[dt.datetime] = acol(storage=S(TZDateTime, nullable=False))

    @op_ctx(alias="par", target="create", arity="collection")
    async def par(cls, ctx):
        from datetime import datetime, timedelta, timezone
        import uuid

        if not settings.enable_rfc9126:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "PAR disabled")
        db = ctx.get("db")
        request = ctx.get("request")
        form = await request.form() if request else {}
        params = dict(form)
        request_uri = f"urn:ietf:params:oauth:request_uri:{uuid.uuid4()}"
        expires_at = datetime.now(tz=timezone.utc) + timedelta(
            seconds=DEFAULT_PAR_EXPIRY
        )
        await cls.handlers.create.core(
            {
                "db": db,
                "payload": {
                    "request_uri": request_uri,
                    "params": params,
                    "expires_at": expires_at,
                },
            }
        )
        return {"request_uri": request_uri, "expires_in": DEFAULT_PAR_EXPIRY}


__all__ = ["PushedAuthorizationRequest"]
