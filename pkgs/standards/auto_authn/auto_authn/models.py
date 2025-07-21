"""
auth_authn_idp.models
=====================
Declarative ORM classes for the Auth + AuthN server (SQLAlchemy 2.x).

Highlights
----------
• **Hard multi‑tenancy** – every row that must be isolated carries a
  ``tenant_id`` FK.
• **Per‑tenant JWKS** – stored as JSON for atomic key rotation.
• **Password hygiene** – bcrypt via *passlib*.
• **API keys** – opaque, hashed, auditable, and revocable.
"""

from __future__ import annotations

import json
import secrets
from datetime import datetime as dt, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from passlib.hash import bcrypt
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID as PG_UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

# --------------------------------------------------------------------------- #
# Base helpers                                                                #
# --------------------------------------------------------------------------- #


class Base(DeclarativeBase):  # noqa: D101
    pass


class TimestampMixin:
    created_at: Mapped[dt] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[dt] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.now(timezone.utc),
        onupdate=lambda: dt.now(timezone.utc),
        nullable=False,
    )


# --------------------------------------------------------------------------- #
# Tenant                                                                      #
# --------------------------------------------------------------------------- #


class Tenant(TimestampMixin, Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    issuer: Mapped[str] = mapped_column(String(255), unique=True)
    jwks_json: Mapped[str] = mapped_column(
        JSONB, comment="Serialized jwkset; first key is the active signer"
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    # ---- Relationships --------------------------------------------------- #
    users: Mapped[List["User"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )
    clients: Mapped[List["Client"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )
    api_keys: Mapped[List["APIKey"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )

    # ---- Convenience ----------------------------------------------------- #
    def jwks_dict(self) -> dict:
        return json.loads(self.jwks_json)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Tenant slug={self.slug} active={self.active}>"

    __table_args__ = (
        Index(
            "ix_tenant_slug_lower",
            slug,
            postgresql_ops={"slug": "text_pattern_ops"},
        ),
    )


# --------------------------------------------------------------------------- #
# User                                                                        #
# --------------------------------------------------------------------------- #


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    sub: Mapped[str] = mapped_column(
        String(64), unique=True, comment="Stable OIDC subject identifier"
    )
    username: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(255))
    _pwd_hash: Mapped[str] = mapped_column("pwd_hash", String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # ---- Relationships --------------------------------------------------- #
    tenant: Mapped["Tenant"] = relationship(back_populates="users")
    api_keys: Mapped[List["APIKey"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )

    # ---- Password helpers ------------------------------------------------ #
    @hybrid_property
    def pwd_hash(self) -> str:  # noqa: D401
        return self._pwd_hash

    def set_password(self, raw: str) -> None:
        self._pwd_hash = bcrypt.hash(raw)

    def verify_password(self, raw: str) -> bool:
        return bcrypt.verify(raw, self._pwd_hash)

    # ---- Convenience ----------------------------------------------------- #
    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.username}@{self.tenant.slug}>"

    __table_args__ = (
        Index(
            "uix_user_username_tenant",
            "tenant_id",
            "username",
            unique=True,
            postgresql_ops={"username": "text_pattern_ops"},
        ),
    )


# --------------------------------------------------------------------------- #
# Client (OIDC RP registration)                                               #
# --------------------------------------------------------------------------- #


class Client(TimestampMixin, Base):
    """
    Registered relying‑party / OIDC client.

    For confidential clients, ``client_secret_hash`` stores SHA‑256 of the
    secret. `jwks_json` may hold public keys for *private_key_jwt* auth.
    """

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    client_secret_hash: Mapped[Optional[bytes]] = mapped_column(
        LargeBinary, nullable=True
    )
    redirect_uris: Mapped[str] = mapped_column(JSONB)
    grant_types: Mapped[List[str]] = mapped_column(
        JSONB, default=lambda: ["authorization_code", "refresh_token"]
    )
    response_types: Mapped[List[str]] = mapped_column(JSONB, default=lambda: ["code"])
    token_endpoint_auth_method: Mapped[str] = mapped_column(
        String(40), default="client_secret_basic"
    )
    jwks_json: Mapped[Optional[str]] = mapped_column(JSONB, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    # ---- Relationships --------------------------------------------------- #
    tenant: Mapped["Tenant"] = relationship(back_populates="clients")

    # ---- Secrets --------------------------------------------------------- #
    def set_client_secret(self, plaintext: str) -> None:
        import hashlib

        self.client_secret_hash = hashlib.sha256(plaintext.encode()).digest()

    def verify_client_secret(self, plaintext: str) -> bool:
        import hashlib

        if self.client_secret_hash is None:
            return False
        return hashlib.sha256(plaintext.encode()).digest() == self.client_secret_hash

    @staticmethod
    def generate_client_id() -> str:  # pragma: no cover
        return secrets.token_urlsafe(16)

    @staticmethod
    def generate_client_secret() -> str:  # pragma: no cover
        return secrets.token_urlsafe(40)

    # ---- Convenience ----------------------------------------------------- #
    def __repr__(self) -> str:  # pragma: no cover
        return f"<Client {self.client_id} (tenant={self.tenant.slug})>"

    __table_args__ = (Index("uix_client_tenant_id", "tenant_id"),)


# --------------------------------------------------------------------------- #
# API Key                                                                     #
# --------------------------------------------------------------------------- #


class APIKey(TimestampMixin, Base):
    """
    Long‑lived Personal‑Access‑Token used as an “API key”.

    The *plaintext* secret is **never** stored – only the first 8‑char prefix
    plus a peppered SHA‑256 digest.  Keys are tenant‑scoped to guarantee hard
    isolation.
    """

    __tablename__ = "api_keys"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    label: Mapped[Optional[str]] = mapped_column(
        String(120), nullable=True, comment="Human‑friendly label"
    )
    prefix: Mapped[str] = mapped_column(
        String(8), nullable=False, comment="First 8 chars of the secret"
    )
    hashed_key: Mapped[str] = mapped_column(String(64), nullable=False)
    scopes: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    expires_at: Mapped[dt] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[Optional[dt]] = mapped_column(DateTime(timezone=True))

    # ---- Relationships --------------------------------------------------- #
    tenant: Mapped["Tenant"] = relationship(back_populates="api_keys")
    owner: Mapped["User"] = relationship(back_populates="api_keys")

    # ---- Convenience ----------------------------------------------------- #
    def is_active(self, now: dt | None = None) -> bool:
        """
        Returns ``True`` if the key is neither expired nor revoked.
        """
        now = now or dt.now(timezone.utc)
        return self.revoked_at is None and self.expires_at > now

    def __repr__(self) -> str:  # pragma: no cover
        return f"<APIKey {self.prefix}… tenant={self.tenant.slug}>"

    __table_args__ = (
        Index(
            "uix_apikey_tenant_prefix",
            "tenant_id",
            "prefix",
            unique=True,
        ),
    )
