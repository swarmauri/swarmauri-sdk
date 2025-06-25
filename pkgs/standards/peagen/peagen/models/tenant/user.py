"""
peagen.models.tenant.user
=========================

SQLAlchemy ORM model for a global User identity.

* Users are **global** (no tenant_id column here).
* Many-to-many membership with Tenant is realised through
  TenantUserAssociation.
"""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import BaseModel


class User(BaseModel):
    """
    A globally unique user who may join any number of tenant workspaces.
    """

    __tablename__ = "users"

    # ──────────────────────── Columns ────────────────────────
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False, default="member")

    # ──────────────────── Relationships ──────────────────────
    tenant_associations: Mapped[list["TenantUserAssociation"]] = relationship(
        "TenantUserAssociation",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Convenience relationship to fetch all tenants a user belongs to
    tenants: Mapped[list["Tenant"]] = relationship(
        "Tenant",
        secondary="tenant_user_associations",
        viewonly=True,
        lazy="selectin",
    )

    # user.py  (add this block)
    repository_associations: Mapped[list["RepositoryUserAssociation"]] = relationship(
        "RepositoryUserAssociation",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    public_keys: Mapped[list["PublicKey"]] = relationship(
        "PublicKey",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # ─────────────────────── Magic ───────────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return f"<User username={self.username!r} email={self.email!r}>"
