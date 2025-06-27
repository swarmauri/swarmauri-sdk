"""
peagen.orm.tenant.tenant
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
    from .tenant_user_association import TenantUserAssociationModel
    from .user import UserModel
    from ..repo.repository import RepositoryModel

# Import at runtime so SQLAlchemy can resolve the relationship target

from ..base import BaseModel  # id, date_created, last_modified mixins


class TenantModel(BaseModel):
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
    user_associations: Mapped[list["TenantUserAssociationModel"]] = relationship(
        "TenantUserAssociationModel",
        back_populates="tenant",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # convenience: direct list of members via the association table
    members: Mapped[list["UserModel"]] = relationship(
        "UserModel",
        secondary="tenant_user_associations",
        viewonly=True,
        lazy="selectin",
    )

    repositories: Mapped[list["RepositoryModel"]] = relationship(
        "RepositoryModel",
        back_populates="tenant",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # ─────────────────────── Magic ───────────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return f"<Tenant slug={self.slug!r} name={self.name!r}>"
