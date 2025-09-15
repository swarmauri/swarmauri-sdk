"""Revoked token model."""

from __future__ import annotations

from tigrbl_auth.deps import (
    Base,
    GUIDPk,
    Timestamped,
    S,
    acol,
    Mapped,
    String,
    op_ctx,
    HTTPException,
    status,
)

from ..runtime_cfg import settings
from ..rfc.rfc7009 import revoke_token as _cache_revoke


class RevokedToken(Base, GUIDPk, Timestamped):
    __tablename__ = "revoked_tokens"
    __table_args__ = ({"schema": "authn"},)

    token: Mapped[str] = acol(
        storage=S(String(512), nullable=False, unique=True, index=True)
    )

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
