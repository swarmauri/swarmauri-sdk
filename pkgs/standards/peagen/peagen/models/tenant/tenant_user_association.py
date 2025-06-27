"""
peagen.models.tenant.tenant_user_association
===========================================

Join table linking global Users to Tenant workspaces.

Naming convention: <Parent><Child>Association  →  TenantUserAssociation
"""

from __future__ import annotations

import uuid
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - imports for type hints
    from .tenant import Tenant
    from .user import User

from ..base import BaseModel


class TenantUserAssociationModel(BaseModel):
    """
    Association row defining a user's membership (and role) within a Tenant.

    Columns
    -------
    tenant_id : UUID
        FK → tenants.id
    user_id   : UUID
        FK → users.id
    role      : str
        Workspace-specific role for the user (owner / admin / member / viewer).
    """

    __tablename__ = "tenant_user_associations"

    # ──────────────────────── Columns ────────────────────────
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String, nullable=False, default="member")

    # ──────────────────── Constraints ────────────────────────
    __table_args__ = (
        UniqueConstraint("tenant_id", "user_id", name="uq_tenant_user_association"),
    )

    # ──────────────────── Relationships ──────────────────────
    tenant: Mapped["Tenant"] = relationship(
        "Tenant", back_populates="user_associations", lazy="selectin"
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="tenant_associations", lazy="selectin"
    )

    # ─────────────────────── Magic ───────────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<TenantUserAssociation tenant_id={self.tenant_id} "
            f"user_id={self.user_id} role={self.role!r}>"
        )


TenantUserAssociation = TenantUserAssociationModel
