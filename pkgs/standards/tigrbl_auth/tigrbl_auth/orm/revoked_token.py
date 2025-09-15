"""Revoked token model."""

from __future__ import annotations

from ..deps import (
    Base,
    Mapped,
    String,
    Timestamped,
    acol,
    op_ctx,
    S,
    HTTPException,
    status,
)

from ..runtime_cfg import settings
from ..rfc.rfc7009 import revoke_token as _cache_revoke


class RevokedToken(Base, Timestamped):
    __tablename__ = "revoked_tokens"
    __table_args__ = ({"schema": "authn"},)

    token: Mapped[str] = acol(storage=S(String(512), primary_key=True))

    @op_ctx(alias="revoke", target="create", arity="collection")
    async def revoke(cls, ctx):
        if not settings.enable_rfc7009:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "revocation disabled")
        db = ctx.get("db")
        payload = ctx.get("payload") or {}
        token = payload.get("token")
        if not token:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "token required")
        await cls.handlers.create.core({"db": db, "payload": {"token": token}})
        _cache_revoke(token)
        return {}


__all__ = ["RevokedToken"]
