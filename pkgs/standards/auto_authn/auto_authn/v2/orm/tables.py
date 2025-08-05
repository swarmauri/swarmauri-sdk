"""
autoapi_authn.orm.tables
~~~~~~~~~~~~~~~~~~~~~~~~

Canonical SQLAlchemy models for the authentication service.

* Tenant  – logical partition; owner of users, clients, keys.
* Client  – OIDC / OAuth2 relying party registration.
* User    – human principal with bcrypt-hashed password.
* ApiKey  – machine credential (digest stored, raw secret shown once).

All models inherit GUIDPk, Timestamped, and (where relevant) TenantBound
from *autoapi.v2.mixins* so they automatically gain:
    • UUID primary keys
    • created_at / updated_at audit stamps
    • row-level security filters via TenantBound
"""

from __future__ import annotations

import re
import uuid
from typing import Annotated, Final

from autoapi.v2 import Base
from autoapi.v2.types import (
    String,
    LargeBinary,
    relationship,
    mapped_column,
    Column,
    PgUUID,
    ForeignKey,
    HookProvider,
)
from autoapi.v2.tables import (
    Tenant as TenantBase,
    Client as ClientBase,
    User as UserBase,
    ApiKey as ApiKeyBase,
)
from autoapi.v2.mixins import (
    GUIDPk,
    Bootstrappable,
    Timestamped,
    TenantBound,
    Principal,
    ActiveToggle,
    Created,
    LastUsed,
    ValidityWindow,
)
from ..crypto import hash_pw  # bcrypt helper shared across package

from hashlib import sha256
from secrets import token_urlsafe
from datetime import datetime, timezone
from fastapi import HTTPException

# ────────────────────────────────────────────────────────────────────
# Utility type alias for 36-char UUID strings
_UUID = Annotated[str, mapped_column(String(36), default=lambda: str(uuid.uuid4()))]

# Regular-expression for a valid client_id (RFC 6749 allows many forms)
_CLIENT_ID_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9\-_]{8,64}$")


class Tenant(TenantBase, Bootstrappable):
    DEFAULT_ROWS = [
        {
            "id": uuid.UUID("FFFFFFFF-0000-0000-0000-000000000000"),
            "email": "tenant@example.com",
            "name": "Public",
            "slug": "public",
        }
    ]


# --------------------------------------------------------------------
class Client(ClientBase):  # Tenant FK via mix-in
    # ----------------------------------------------------------------
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
        secret_hash = hash_pw(client_secret)
        return cls(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret_hash=secret_hash,
            redirect_uris=" ".join(redirects),
        )

    def verify_secret(self, plain: str) -> bool:
        from ..crypto import verify_pw  # local import to avoid cycle

        return verify_pw(plain, self.client_secret_hash)


# --------------------------------------------------------------------
class User(UserBase):
    """Human principal with authentication credentials."""

    __table_args__ = {"extend_existing": True}
    email = Column(String(120), unique=True)
    password_hash = Column(LargeBinary(60))
    api_keys = relationship(
        "auto_authn.v2.orm.tables.ApiKey",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # ----------------------------------------------------------------
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


class Service(Base, GUIDPk, Timestamped, TenantBound, Principal, ActiveToggle):
    """Machine principal representing an automated service."""

    __tablename__ = "services"

    name = Column(String(120), unique=True, nullable=False)
    api_keys = relationship(
        "auto_authn.v2.orm.tables.ServiceKey",
        back_populates="service",
        cascade="all, delete-orphan",
    )


class ApiKey(ApiKeyBase, HookProvider):
    user = relationship(
        "auto_authn.v2.orm.tables.User",
        back_populates="api_keys",
        lazy="joined",  # optional: eager load to avoid N+1
    )

    @staticmethod
    def digest_of(value: str) -> None:
        return sha256(value.encode()).hexdigest()

    @classmethod
    async def _pre_create_generate(cls, ctx):
        params = ctx["env"].params
        raw = token_urlsafe(32)
        digest = sha256(raw.encode()).hexdigest()
        now = datetime.now(timezone.utc)
        if hasattr(params, "model_dump"):
            if getattr(params, "raw_key", None) or getattr(params, "digest", None):
                raise HTTPException(
                    status_code=422, detail="raw_key/digest are server generated"
                )
            params = params.model_copy(update={"digest": digest, "last_used_at": now})
            ctx["env"].params = params
        elif isinstance(params, dict):
            if params.get("raw_key") or params.get("digest"):
                raise HTTPException(
                    status_code=422, detail="raw_key/digest are server generated"
                )
            params["digest"] = digest
            params["last_used_at"] = now
        ctx["raw_api_key"] = raw

    @classmethod
    async def _post_create_inject_key(cls, ctx):
        raw = ctx.get("raw_api_key")
        if not raw:
            return
        result = dict(ctx.get("result", {}))
        result["api_key"] = raw
        ctx["result"] = result

    @classmethod
    def __autoapi_register_hooks__(cls, api) -> None:
        from autoapi.v2 import Phase

        api.register_hook(Phase.PRE_TX_BEGIN, model="ApiKey", op="create")(
            cls._pre_create_generate
        )
        api.register_hook(Phase.POST_COMMIT, model="ApiKey", op="create")(
            cls._post_create_inject_key
        )


class ServiceKey(
    Base,
    GUIDPk,
    Created,
    LastUsed,
    ValidityWindow,
    HookProvider,
):
    __tablename__ = "service_keys"

    service_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("services.id"),
        index=True,
        nullable=False,
    )
    label = Column(String(120), nullable=False)

    digest = Column(
        String(64),
        nullable=False,
        unique=True,
        info={
            "autoapi": {
                # still excluded from create/update schemas
                "disable_on": ["create", "update", "replace"],
                "read_only": True,
            }
        },
    )

    service = relationship(
        "auto_authn.v2.orm.tables.Service",
        back_populates="api_keys",
        lazy="joined",
    )

    @staticmethod
    def digest_of(value: str) -> str:
        return sha256(value.encode()).hexdigest()
        
    # ──────────────────────────────────────────────────────────
    # Hooks
    # ──────────────────────────────────────────────────────────
    @classmethod
    async def _pre_commit_generate(cls, ctx):
        """
        • Runs just before flush/commit on *create*.
        • Generates a raw key, hashes it into `digest`,
          and stores both on the SQLAlchemy row.
        • Stashes the raw key in ctx so POST_COMMIT can expose it.
        """
        row = ctx["row"]                      # SQLAlchemy instance
        if row.digest:                        # idempotence guard
            return

        raw   = token_urlsafe(32)
        row.digest        = cls.digest_of(raw)
        row.last_used_at  = datetime.now(timezone.utc)
        ctx["raw_service_key"] = raw          # pass downstream

    @classmethod
    async def _post_commit_inject(cls, ctx):
        """
        After the transaction commits, swap the digest back out
        and give the caller the one-time secret.
        """
        raw = ctx.pop("raw_service_key", None)
        if raw:
            result = dict(ctx.get("result", {}))
            result["service_key"] = raw
            ctx["result"] = result

    # ──────────────────────────────────────────────────────────
    # Hook registration
    # ──────────────────────────────────────────────────────────
    @classmethod
    def __autoapi_register_hooks__(cls, api) -> None:
        from autoapi.v2 import Phase

        api.register_hook(
            Phase.PRE_COMMIT, model="ServiceKey", op="create"
        )(cls._pre_commit_generate)

        api.register_hook(
            Phase.POST_COMMIT, model="ServiceKey", op="create"
        )(cls._post_commit_inject)


__all__ = [
    "ApiKey",
    "ServiceKey",
    "User",
    "Service",
    "Tenant",
    "Client",
]
