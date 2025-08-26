"""Authentication session model."""

from __future__ import annotations

import datetime as dt

from autoapi.v3.tables import Base
from autoapi.v3.mixins import TenantMixin, Timestamped, UserMixin
from autoapi.v3.specs import S, acol
from autoapi.v3.types import String, TZDateTime
from autoapi.v3 import op_ctx, hook_ctx
from fastapi import HTTPException


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
    def login(cls, ctx):
        pass

    @op_ctx(alias="logout", target="delete", arity="member")
    def logout(cls, ctx, obj):
        return obj


__all__ = ["AuthSession"]
