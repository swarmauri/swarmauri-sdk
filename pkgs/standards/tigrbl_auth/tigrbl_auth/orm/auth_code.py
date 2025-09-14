"""Authorization code model."""

from __future__ import annotations

import datetime as dt
import uuid

from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import TenantColumn, Timestamped, UserColumn
from tigrbl.specs import S, acol
from tigrbl.column.storage_spec import ForeignKeySpec
from tigrbl.types import JSON, PgUUID, String, TZDateTime, Mapped, UUID
from tigrbl import op_ctx
from fastapi import HTTPException, status

from ..rfc8414_metadata import ISSUER
from ..oidc_id_token import mint_id_token, oidc_hash
from ..rfc7636_pkce import verify_code_challenge
from ..routers.shared import _jwt, _require_tls
from .user import User


class AuthCode(Base, Timestamped, UserColumn, TenantColumn):
    __tablename__ = "auth_codes"
    __table_args__ = ({"schema": "authn"},)

    code: Mapped[uuid.UUID] = acol(storage=S(PgUUID(as_uuid=True), primary_key=True))
    client_id: Mapped[uuid.UUID] = acol(
        storage=S(
            PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="authn.clients.id"),
            nullable=False,
        )
    )
    redirect_uri: Mapped[str] = acol(storage=S(String(1000), nullable=False))
    code_challenge: Mapped[str | None] = acol(storage=S(String, nullable=True))
    nonce: Mapped[str | None] = acol(storage=S(String, nullable=True))
    scope: Mapped[str | None] = acol(storage=S(String, nullable=True))
    expires_at: Mapped[dt.datetime] = acol(storage=S(TZDateTime, nullable=False))
    claims: Mapped[dict | None] = acol(storage=S(JSON, nullable=True))

    @op_ctx(alias="exchange", target="delete", arity="member")
    async def exchange(cls, ctx, obj):
        import secrets
        from datetime import datetime

        request = ctx.get("request")
        _require_tls(request)
        db = ctx.get("db")
        payload = ctx.get("payload") or {}
        client_id = payload.get("client_id")
        redirect_uri = payload.get("redirect_uri")
        verifier = payload.get("code_verifier")

        def _normalize(val: str | None) -> str | None:
            if val is None:
                return None
            try:
                u = UUID(val)
            except ValueError:
                u = UUID(hex=val)
            pg = PgUUID(as_uuid=True)
            pg.as_uuid = u
            return pg.hex

        if (
            obj is None
            or obj.client_id.hex != _normalize(client_id)
            or obj.redirect_uri != redirect_uri
            or datetime.utcnow() > obj.expires_at
        ):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "invalid_grant"})
        if obj.code_challenge and not (
            verifier and verify_code_challenge(verifier, obj.code_challenge)
        ):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "invalid_grant"})
        jwt_kwargs: dict[str, str] = {}
        if obj.scope:
            jwt_kwargs["scope"] = obj.scope
        access, refresh = await _jwt.async_sign_pair(
            sub=str(obj.user_id), tid=str(obj.tenant_id), **jwt_kwargs
        )
        nonce = obj.nonce or secrets.token_urlsafe(8)
        extra_claims: dict[str, str] = {
            "tid": str(obj.tenant_id),
            "typ": "id",
            "at_hash": oidc_hash(access),
        }
        if obj.claims and "id_token" in obj.claims:
            user_obj = await db.get(User, obj.user_id)
            idc = obj.claims["id_token"]
            if "email" in idc:
                extra_claims["email"] = user_obj.email if user_obj else ""
            if any(k in idc for k in ("name", "preferred_username")):
                extra_claims["name"] = user_obj.username if user_obj else ""
        id_token = await mint_id_token(
            sub=str(obj.user_id),
            aud=client_id,
            nonce=nonce,
            issuer=ISSUER,
            **extra_claims,
        )
        await cls.handlers.delete.core({"db": db, "obj": obj})
        return {
            "access_token": access,
            "refresh_token": refresh,
            "id_token": id_token,
        }


__all__ = ["AuthCode"]
