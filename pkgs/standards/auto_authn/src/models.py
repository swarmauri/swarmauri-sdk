"""
auth_authn_idp.models
=====================
Declarative ORM classes for the Auth + AuthN server.

Design highlights
-----------------
* **Multi‑tenant isolation** – every user and client row carries a `tenant_id` FK.
* **Per‑tenant JWKS** – stored as JSON (`jwks_json`) so key‑rotation is atomic.
* **Password hygiene** – hashes via `passlib[bcrypt]`; helpers on the `User` model.
* **Timestamps + soft‑delete** – `TimestampMixin` plus `active` boolean flags.
"""

from __future__ import annotations

import json
import secrets
from datetime import datetime as dt, timezone
from typing import List, Optional

from passlib.hash import bcrypt
from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# --------------------------------------------------------------------------- #
# Base helpers                                                                #
# --------------------------------------------------------------------------- #


class Base(DeclarativeBase):  # noqa: D101  (naming in one place)
    pass


class TimestampMixin:
    created_at: Mapped[dt] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.now(timezone.utc), nullable=False
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
        JSON, comment="Serialized jwkset; first key is the active signer"
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    # ---- Relationships --------------------------------------------------- #
    users: Mapped[List["User"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )
    clients: Mapped[List["Client"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )

    # ---- Convenience ----------------------------------------------------- #
    def jwks_dict(self) -> dict:
        "Return jwkset as Python dict (not string)."
        return json.loads(self.jwks_json)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Tenant slug={self.slug} active={self.active}>"

    # Composite unique constraint: optional if you need both fields unique
    __table_args__ = (
        Index("ix_tenant_slug_lower", slug, postgresql_ops={"slug": "text_pattern_ops"}),
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

    # ---- Password helpers ------------------------------------------------ #
    @hybrid_property
    def pwd_hash(self) -> str:
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

    `client_secret_hash` stores SHA‑256 of the secret for confidential clients.
    For `private_key_jwt` authentication you can store PEM public key in
    `jwks_json`.
    """

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    client_secret_hash: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    redirect_uris: Mapped[str] = mapped_column(
        JSON, comment="List[str] of registered redirect URIs"
    )
    grant_types: Mapped[List[str]] = mapped_column(
        JSON, default=lambda: ["authorization_code", "refresh_token"]
    )
    response_types: Mapped[List[str]] = mapped_column(
        JSON, default=lambda: ["code"]
    )
    token_endpoint_auth_method: Mapped[str] = mapped_column(
        String(40), default="client_secret_basic"
    )
    jwks_json: Mapped[Optional[str]] = mapped_column(
        JSON, nullable=True, comment="Public keys for private_key_jwt auth"
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    # ---- Relationships --------------------------------------------------- #
    tenant: Mapped["Tenant"] = relationship(back_populates="clients")

    # ---- Secrets --------------------------------------------------------- #
    def set_client_secret(self, plaintext: str) -> None:
        """
        Store SHA‑256 digest of client_secret.  The plaintext never touches DB.
        """
        import hashlib

        self.client_secret_hash = hashlib.sha256(plaintext.encode()).digest()

    def verify_client_secret(self, plaintext: str) -> bool:
        import hashlib

        if self.client_secret_hash is None:
            return False
        return (
            hashlib.sha256(plaintext.encode()).digest() == self.client_secret_hash
        )

    @staticmethod
    def generate_client_id() -> str:  # pragma: no cover
        return secrets.token_urlsafe(16)

    @staticmethod
    def generate_client_secret() -> str:  # pragma: no cover
        return secrets.token_urlsafe(40)

    # ---- Convenience ----------------------------------------------------- #
    def __repr__(self) -> str:  # pragma: no cover
        return f"<Client {self.client_id} (tenant={self.tenant.slug})>"

    __table_args__ = (
        Index("uix_client_tenant_id", "tenant_id"),
    )
