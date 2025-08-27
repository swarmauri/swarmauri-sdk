"""Authentication session model."""

from __future__ import annotations

import datetime as dt

from autoapi.v3.tables import Base
from autoapi.v3.mixins import TenantMixin, Timestamped, UserMixin
from autoapi.v3.specs import S, acol
from autoapi.v3.types import String, TZDateTime
from autoapi.v3 import op_ctx, hook_ctx
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse, Response


class AuthSession(Base, Timestamped, UserMixin, TenantMixin):
    __tablename__ = "sessions"
    __table_args__ = ({"schema": "authn"},)

    id: str = acol(storage=S(String(64), primary_key=True))
    username: str = acol(storage=S(String(120), nullable=False))
    auth_time: dt.datetime = acol(
        storage=S(
            TZDateTime, nullable=False, default=lambda: dt.datetime.now(dt.timezone.utc)
        )
    )

    @hook_ctx(ops="login", phase="PRE_HANDLER")
    async def _verify_credentials(cls, ctx):
        from .user import User

        payload = ctx.get("payload") or {}
        db = ctx.get("db")
        username = payload.get("username")
        password = payload.get("password")
        if db is None or not username or not password:
            raise HTTPException(status_code=400, detail="missing credentials")

        users = await User.handlers.list.core(
            {"db": db, "payload": {"filters": {"username": username}}}
        )
        user = users.items[0] if getattr(users, "items", None) else None
        if user is None or not user.verify_password(password):
            raise HTTPException(status_code=400, detail="invalid credentials")

        payload.pop("password", None)
        payload["user_id"] = user.id
        payload["tenant_id"] = user.tenant_id
        payload["username"] = user.username

    @op_ctx(alias="login", target="create", arity="collection")
    async def login(cls, ctx):
        import secrets
        from ..rfc8414_metadata import ISSUER
        from ..oidc_id_token import mint_id_token
        from ..routers.shared import (
            _jwt,
            _require_tls,
            SESSIONS,
        )

        request = ctx.get("request")
        _require_tls(request)
        db = ctx.get("db")
        payload = ctx.get("payload") or {}
        session_id = payload.get("id") or secrets.token_urlsafe(16)
        payload["id"] = session_id
        session = await cls.handlers.create.core({"db": db, "payload": payload})
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
        id_token = mint_id_token(
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

    @op_ctx(alias="logout", target="delete", arity="collection")
    async def logout(cls, ctx):
        from ..rfc8414_metadata import ISSUER
        from ..oidc_id_token import verify_id_token
        from ..routers.shared import (
            _require_tls,
            _front_channel_logout,
            _back_channel_logout,
            SESSIONS,
        )

        request = ctx.get("request")
        _require_tls(request)
        db = ctx.get("db")
        payload = ctx.get("payload") or {}
        id_hint = payload.get("id_token_hint")
        try:
            claims = verify_id_token(id_hint, issuer=ISSUER, audience=ISSUER)
        except Exception as exc:  # pragma: no cover - passthrough
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "invalid id_token_hint"
            ) from exc
        sid = claims.get("sid")
        if sid:
            session = await cls.handlers.read.core({"db": db, "obj_id": sid})
            if session:
                await cls.handlers.delete.core({"db": db, "obj": session})
            SESSIONS.pop(sid, None)
            await _front_channel_logout(sid)
            await _back_channel_logout(sid)
        response = Response(status_code=status.HTTP_204_NO_CONTENT)
        response.delete_cookie("sid")
        return response


__all__ = ["AuthSession"]
