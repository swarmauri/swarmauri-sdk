"""User model for the authentication service."""

from __future__ import annotations

import uuid

from autoapi.v3.orm.tables import User as UserBase
from autoapi.v3 import hook_ctx, op_ctx
from ..routers.schemas import RegisterIn, TokenPair
from autoapi.v3.types import LargeBinary, Mapped, String, relationship
from autoapi.v3.specs import F, IO, S, acol, ColumnSpec
from typing import TYPE_CHECKING

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select

if TYPE_CHECKING:  # pragma: no cover
    pass


class User(UserBase):
    """Human principal with authentication credentials."""

    __table_args__ = ({"extend_existing": True, "schema": "authn"},)
    username: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(String(32), nullable=False),
            field=F(constraints={"max_length": 32}, required_in=("create",)),
            io=IO(
                in_verbs=("create", "update", "replace"),
                out_verbs=("read", "list"),
                filter_ops=("eq", "ilike"),
                sortable=True,
            ),
        )
    )
    email: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(String(120), nullable=False, unique=True),
            field=F(constraints={"max_length": 120}, required_in=("create",)),
            io=IO(
                in_verbs=("create", "update", "replace"),
                out_verbs=("read", "list"),
                filter_ops=("eq", "ilike"),
                sortable=True,
            ),
        )
    )
    password_hash: Mapped[bytes | None] = acol(
        spec=ColumnSpec(
            storage=S(LargeBinary(60)),
            io=IO(in_verbs=("create", "update", "replace")),
        )
    )
    _api_keys = relationship(
        "ApiKey",
        back_populates="_user",
        cascade="all, delete-orphan",
    )

    @hook_ctx(ops=("create",), phase="PRE_VALIDATE")
    async def _resolve_tenant_slug(cls, ctx):
        payload = ctx.get("payload") or {}
        slug = payload.pop("tenant_slug", None)
        if slug:
            from .tenant import Tenant

            db = ctx.get("db")
            tenant = await db.scalar(select(Tenant).where(Tenant.slug == slug).limit(1))
            if tenant is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "tenant not found")
            payload["tenant_id"] = tenant.id

    @hook_ctx(ops=("create", "update"), phase="PRE_HANDLER")
    async def _hash_password(cls, ctx):
        payload = ctx.get("payload") or {}
        plain = payload.pop("password", None)
        if plain:
            from ..crypto import hash_pw

            payload["password_hash"] = hash_pw(plain)

    @op_ctx(
        alias="register",
        target="create",
        arity="collection",
        request_schema=RegisterIn,
        response_schema=TokenPair,
    )
    async def register(cls, ctx):
        import secrets
        from ..rfc8414_metadata import ISSUER
        from ..oidc_id_token import mint_id_token
        from ..routers.shared import _jwt, _require_tls, SESSIONS
        from .auth_session import AuthSession
        from .tenant import Tenant
        from autoapi.v3.error import IntegrityError

        request = ctx.get("request")
        _require_tls(request)
        db = ctx.get("db")
        payload = ctx.get("payload") or {}
        plain_pw = payload.get("password")
        try:
            tenant_slug = payload.pop("tenant_slug")
            tenant = await db.scalar(
                select(Tenant).where(Tenant.slug == tenant_slug).limit(1)
            )
            if tenant is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "tenant not found")
            payload["tenant_id"] = tenant.id
            await cls.handlers.create.core({"db": db, "payload": payload})
            session_id = secrets.token_urlsafe(16)
            session = await AuthSession.handlers.login.core(
                {
                    "db": db,
                    "payload": {
                        "id": session_id,
                        "username": payload["username"],
                        "password": plain_pw,
                    },
                }
            )
        except HTTPException:
            raise
        except Exception as exc:  # pragma: no cover - passthrough
            if isinstance(exc, IntegrityError):
                raise HTTPException(status.HTTP_409_CONFLICT, "duplicate key") from exc
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, "database error"
            ) from exc

        access, refresh = await _jwt.async_sign_pair(
            sub=str(session.user_id),
            tid=str(session.tenant_id),
            scope="openid profile email",
        )
        SESSIONS[session.id] = {
            "sub": str(session.user_id),
            "tid": str(session.tenant_id),
            "username": session.username,
            "auth_time": session.auth_time,
        }
        id_token = await mint_id_token(
            sub=str(session.user_id),
            aud=ISSUER,
            nonce=secrets.token_urlsafe(8),
            issuer=ISSUER,
            sid=session.id,
        )
        pair = {
            "access_token": access,
            "refresh_token": refresh,
            "id_token": id_token,
        }
        response = JSONResponse(pair)
        response.set_cookie("sid", session.id, httponly=True, samesite="lax")
        return response

    @classmethod
    def new(cls, tenant_id: uuid.UUID, username: str, email: str, password: str):
        return cls(
            tenant_id=tenant_id,
            username=username,
            email=email,
        )

    def verify_password(self, plain: str) -> bool:
        from ..crypto import verify_pw

        return verify_pw(plain, self.password_hash)


__all__ = ["User"]
