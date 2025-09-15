"""User model for the authentication service."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from tigrbl_auth.deps import (
    UserBase,
    hook_ctx,
    op_ctx,
    LargeBinary,
    Mapped,
    String,
    relationship,
    F,
    IO,
    S,
    acol,
    ColumnSpec,
    HTTPException,
    status,
)
from ..routers.schemas import RegisterIn, TokenPair

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
    tenant = relationship("Tenant", back_populates="users")

    @hook_ctx(ops=("create", "update", "register"), phase="PRE_HANDLER")
    async def _resolve_tenant_slug(cls, ctx):
        payload = ctx.get("payload") or {}
        slug = payload.pop("tenant_slug", None)
        if slug:
            from .tenant import Tenant

            db = ctx.get("db")
            tenants = await Tenant.handlers.list.core(
                {"db": db, "payload": {"filters": {"slug": slug}}}
            )
            tenant = tenants.items[0] if getattr(tenants, "items", None) else None
            if tenant is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "tenant not found")
            payload["tenant_id"] = tenant.id

    @hook_ctx(ops=("create", "update", "register"), phase="PRE_HANDLER")
    async def _hash_password(cls, ctx):
        payload = ctx.get("payload") or {}
        if not payload.get("password"):
            request = ctx.get("request")
            if request is not None:
                try:
                    body = await request.json()
                except Exception:  # pragma: no cover - unexpected
                    body = {}
                payload.update(body)
        plain = payload.pop("password", None)
        if plain:
            from ..crypto import hash_pw

            payload["password_hash"] = hash_pw(plain)

    @op_ctx(
        alias="register",
        target="custom",
        arity="collection",
        request_schema=RegisterIn,
        response_schema=TokenPair,
    )
    async def register(cls, ctx):
        from ..routers.shared import _require_tls
        from .auth_session import AuthSession
        from .tenant import Tenant
        from tigrbl_auth.deps import IntegrityError

        request = ctx.get("request")
        _require_tls(request)
        db = ctx.get("db")
        payload = ctx.get("payload") or {}
        plain_pw = payload.get("password")
        try:
            tenant_slug = payload.pop("tenant_slug")
            tenants = await Tenant.handlers.list.core(
                {"db": db, "payload": {"filters": {"slug": tenant_slug}}}
            )
            tenant = tenants.items[0] if getattr(tenants, "items", None) else None
            if tenant is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "tenant not found")
            payload["tenant_id"] = tenant.id

            await cls.handlers.create.core({"db": db, "payload": payload})
            ctx_login = {
                "db": db,
                "payload": {
                    "username": payload["username"],
                    "password": plain_pw,
                },
                "request": request,
            }
            return await AuthSession.handlers.login.core(ctx_login)
        except HTTPException:
            raise
        except Exception as exc:  # pragma: no cover - passthrough
            if isinstance(exc, IntegrityError):
                raise HTTPException(status.HTTP_409_CONFLICT, "duplicate key") from exc
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, "database error"
            ) from exc

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
