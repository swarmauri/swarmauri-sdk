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
    UserMixin,
)
from ..crypto import hash_pw  # bcrypt helper shared across package


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
    service_keys = relationship(
        "auto_authn.v2.orm.tables.ServiceKey",
        back_populates="service",
        cascade="all, delete-orphan",
    )


class ApiKey(ApiKeyBase, UserMixin):
    __table_args__ = {"extend_existing": True}

    user = relationship(
        "auto_authn.v2.orm.tables.User",
        back_populates="api_keys",
        lazy="joined",  # optional: eager load to avoid N+1
    )


class ServiceKey(ApiKeyBase):
    __tablename__ = "service_keys"
    
    service_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("services.id"),
        index=True,
        nullable=False,
    )

    service = relationship(
        "auto_authn.v2.orm.tables.Service",
        back_populates="service_keys",
        lazy="joined",
    )


__all__ = [
    "ApiKey",
    "ServiceKey",
    "User",
    "Service",
    "Tenant",
    "Client",
]
