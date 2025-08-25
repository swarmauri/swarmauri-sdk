"""
autoapi_authn.v2.orm.tables
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

import datetime as dt
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
    UniqueConstraint,
    JSON,
    Boolean,
    Integer,
    TZDateTime,
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
from ..rfc8252 import validate_native_redirect_uri
from ..runtime_cfg import settings


# ────────────────────────────────────────────────────────────────────
# Utility type alias for 36-char UUID strings
_UUID = Annotated[str, mapped_column(String(36), default=lambda: str(uuid.uuid4()))]

# Regular-expression for a valid client_id (RFC 6749 allows many forms)
_CLIENT_ID_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9\-_]{8,64}$")


class Tenant(TenantBase, Bootstrappable):
    # __mapper_args__ = {"concrete": True}
    __table_args__ = (
        {
            "extend_existing": True,
            "schema": "authn",
        },
    )
    name = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
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
    __table_args__ = ({"schema": "authn"},)

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
        if settings.enforce_rfc8252:
            for uri in redirects:
                validate_native_redirect_uri(uri)
        secret_hash = hash_pw(client_secret)
        return cls(
            tenant_id=tenant_id,
            id=client_id,
            client_secret_hash=secret_hash,
            redirect_uris=" ".join(redirects),
        )

    def verify_secret(self, plain: str) -> bool:
        from ..crypto import verify_pw  # local import to avoid cycle

        return verify_pw(plain, self.client_secret_hash)


# --------------------------------------------------------------------
class User(UserBase):
    """Human principal with authentication credentials."""

    __table_args__ = ({"extend_existing": True, "schema": "authn"},)
    email = Column(String(120), nullable=False, unique=True)
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
    __table_args__ = ({"schema": "authn"},)
    name = Column(String(120), unique=True, nullable=False)
    service_keys = relationship(
        "auto_authn.v2.orm.tables.ServiceKey",
        back_populates="service",
        cascade="all, delete-orphan",
    )


class ApiKey(ApiKeyBase, UserMixin):
    __table_args__ = (
        UniqueConstraint("digest"),
        {"extend_existing": True, "schema": "authn"},
    )

    user = relationship(
        "auto_authn.v2.orm.tables.User",
        back_populates="api_keys",
        lazy="joined",  # optional: eager load to avoid N+1
    )


class ServiceKey(ApiKeyBase):
    __tablename__ = "service_keys"
    __table_args__ = (
        UniqueConstraint("digest"),
        {"extend_existing": True, "schema": "authn"},
    )
    service_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("authn.services.id"),
        index=True,
        nullable=False,
    )

    service = relationship(
        "auto_authn.v2.orm.tables.Service",
        back_populates="service_keys",
        lazy="joined",
    )


class AuthSession(Base, Timestamped):
    __tablename__ = "sessions"
    __table_args__ = ({"schema": "authn"},)

    id = Column(String(64), primary_key=True)
    user_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("authn.users.id"),
        nullable=False,
        index=True,
    )
    tenant_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("authn.tenants.id"),
        nullable=False,
        index=True,
    )
    username = Column(String(120), nullable=False)
    auth_time = Column(
        TZDateTime, default=lambda: dt.datetime.now(dt.timezone.utc), nullable=False
    )


class AuthCode(Base, Timestamped):
    __tablename__ = "auth_codes"
    __table_args__ = ({"schema": "authn"},)

    code = Column(String(128), primary_key=True)
    user_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("authn.users.id"),
        nullable=False,
        index=True,
    )
    tenant_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("authn.tenants.id"),
        nullable=False,
        index=True,
    )
    client_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("authn.clients.id"),
        nullable=False,
    )
    redirect_uri = Column(String(1000), nullable=False)
    code_challenge = Column(String, nullable=True)
    nonce = Column(String, nullable=True)
    scope = Column(String, nullable=True)
    expires_at = Column(TZDateTime, nullable=False)
    claims = Column(JSON, nullable=True)


class DeviceCode(Base, Timestamped):
    __tablename__ = "device_codes"
    __table_args__ = ({"schema": "authn"},)

    device_code = Column(String(128), primary_key=True)
    user_code = Column(String(32), nullable=False, index=True)
    client_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("authn.clients.id"),
        nullable=False,
    )
    expires_at = Column(TZDateTime, nullable=False)
    interval = Column(Integer, nullable=False)
    authorized = Column(Boolean, default=False, nullable=False)
    user_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("authn.users.id"),
        nullable=True,
        index=True,
    )
    tenant_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("authn.tenants.id"),
        nullable=True,
        index=True,
    )


class RevokedToken(Base, Timestamped):
    __tablename__ = "revoked_tokens"
    __table_args__ = ({"schema": "authn"},)

    token = Column(String(512), primary_key=True)


class PushedAuthorizationRequest(Base, Timestamped):
    __tablename__ = "par_requests"
    __table_args__ = ({"schema": "authn"},)

    request_uri = Column(String(255), primary_key=True)
    params = Column(JSON, nullable=False)
    expires_at = Column(TZDateTime, nullable=False)


__all__ = [
    "ApiKey",
    "ServiceKey",
    "User",
    "Service",
    "Tenant",
    "Client",
    "AuthSession",
    "AuthCode",
    "DeviceCode",
    "RevokedToken",
    "PushedAuthorizationRequest",
]
