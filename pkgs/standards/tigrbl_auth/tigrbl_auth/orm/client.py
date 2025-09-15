"""Client model for the authentication service."""

from __future__ import annotations

import re
import uuid
from typing import Final
from urllib.parse import urlparse

from tigrbl_auth.deps import (
    hook_ctx,
    op_ctx,
    ClientBase,
    relationship,
    HTTPException,
    status,
    Mapped,
    String,
    ColumnSpec,
    F,
    IO,
    S,
    acol,
)

from ..crypto import hash_pw
from ..rfc.rfc8252 import (
    RFC8252_SPEC_URL,
    is_native_redirect_uri,
    validate_native_redirect_uri,
)
from ..runtime_cfg import settings

_CLIENT_ID_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9\-_]{8,64}$")


class Client(ClientBase):
    __table_args__ = ({"schema": "authn"},)

    tenant = relationship("Tenant", back_populates="clients")

    grant_types: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(String, nullable=False, default="authorization_code"),
            field=F(),
            io=IO(),
        )
    )
    response_types: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(String, nullable=False, default="code"),
            field=F(),
            io=IO(),
        )
    )

    @hook_ctx(ops=("create", "update", "register"), phase="PRE_HANDLER")
    async def _hash_secret(cls, ctx):
        payload = ctx.get("payload") or {}
        secret = payload.pop("client_secret", None)
        if secret:
            payload["client_secret_hash"] = hash_pw(secret)

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

    @classmethod
    def new(
        cls,
        tenant_id: uuid.UUID,
        client_id: str,
        client_secret: str,
        redirects: list[str],
    ):
        if not _CLIENT_ID_RE.fullmatch(client_id):
            raise ValueError("invalid client_id format")
        if settings.enforce_rfc8252:
            for uri in redirects:
                parsed = urlparse(uri)
                if is_native_redirect_uri(uri):
                    validate_native_redirect_uri(uri)
                elif parsed.scheme == "http":
                    raise ValueError(
                        f"redirect URI not permitted for native apps per RFC 8252: {RFC8252_SPEC_URL}"
                    )
        secret_hash = hash_pw(client_secret)
        try:
            obj_id: uuid.UUID | str = uuid.UUID(client_id)
        except ValueError:
            obj_id = client_id
        return cls(
            tenant_id=tenant_id,
            id=obj_id,
            client_secret_hash=secret_hash,
            redirect_uris=" ".join(redirects),
        )

    @op_ctx(
        alias="register",
        target="create",
        arity="collection",
        status_code=status.HTTP_201_CREATED,
    )
    async def register(cls, ctx):
        import secrets

        from urllib.parse import urlparse

        db = ctx.get("db")
        payload = ctx.get("payload") or {}
        redirects = payload.get("redirect_uris") or []
        if isinstance(redirects, list):
            for uri in redirects:
                parsed = urlparse(uri)
                if parsed.scheme != "https" and parsed.hostname not in {
                    "localhost",
                    "127.0.0.1",
                    "::1",
                }:
                    raise HTTPException(
                        status.HTTP_400_BAD_REQUEST,
                        "redirect URIs must use https scheme",
                    )
            payload["redirect_uris"] = " ".join(redirects)
        grant_types = payload.get("grant_types")
        if isinstance(grant_types, list):
            payload["grant_types"] = " ".join(grant_types)
        else:
            payload.setdefault("grant_types", "authorization_code")
        response_types = payload.get("response_types")
        if isinstance(response_types, list):
            payload["response_types"] = " ".join(response_types)
        else:
            payload.setdefault("response_types", "code")
        client_id = payload.get("client_id") or secrets.token_urlsafe(16)
        payload["id"] = client_id
        secret = payload.get("client_secret") or secrets.token_urlsafe(32)
        payload["client_secret"] = secret
        obj = await cls.handlers.create.core({"db": db, "payload": payload})
        return {
            "client_id": str(obj.id),
            "client_secret": secret,
            "redirect_uris": obj.redirect_uris.split(),
            "grant_types": obj.grant_types.split(),
            "response_types": obj.response_types.split(),
        }

    def verify_secret(self, plain: str) -> bool:
        from ..crypto import verify_pw  # local import to avoid cycle

        return verify_pw(plain, self.client_secret_hash)


__all__ = ["Client", "_CLIENT_ID_RE"]
