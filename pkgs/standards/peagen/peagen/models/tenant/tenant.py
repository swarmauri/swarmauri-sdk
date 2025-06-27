"""
peagen.models.tenant.tenant
===========================

SQLAlchemy model for the Tenant domain object.

• One-to-many: Tenant ➜ User                 (via `users`)
• One-to-many: Tenant ➜ TenantUserAssociation (via `user_associations`)
"""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - imports for type hints
    from .tenant_user_association import TenantUserAssociation
    from .user import User
    from ..repo.repository import Repository

from ..base import BaseModel  # id, date_created, last_modified mixins


class Tenant(BaseModel):
    """
    Represents an organizational boundary (company, team, project-space).

    Columns
    -------
    slug : str
        URL-safe unique identifier (e.g., "acme").
    name : str
        Human-readable tenant name.
    """

    __tablename__ = "tenants"

    # ──────────────────────── Columns ────────────────────────
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

    # ──────────────────── Relationships ──────────────────────
    # full association rows (contains role etc.)
    user_associations: Mapped[list["TenantUserAssociation"]] = relationship(
        "TenantUserAssociation",
        back_populates="tenant",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # convenience: direct list of members via the association table
    members: Mapped[list["User"]] = relationship(
        "User",
        secondary="tenant_user_associations",
        viewonly=True,
        lazy="selectin",
    )

    repositories: Mapped[list["Repository"]] = relationship(
        "Repository",
        back_populates="tenant",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # ─────────────────────── Magic ───────────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return f"<Tenant slug={self.slug!r} name={self.name!r}>"
