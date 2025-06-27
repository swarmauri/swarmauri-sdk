"""
peagen.models.repo.repository_user_association
=============================================

Join table that grants a global User a role on a specific Repository.

Columns
-------
repository_id : UUID   – FK → repositories.id
user_id       : UUID   – FK → users.id
role          : str    – 'admin' | 'write' | 'read'  (default = 'read')
"""

from __future__ import annotations

import uuid
from sqlalchemy import String, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - imports for type hints
    from .repository import Repository
    from ..tenant.user import User

from ..base import BaseModel


class RepositoryUserAssociationModel(BaseModel):
    __tablename__ = "repository_user_associations"

    # ──────────────────────── Columns ────────────────────────
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="read",
        doc="Per-repository role: read / write / admin",
    )

    # ──────────────────── Constraints ────────────────────────
    __table_args__ = (
        UniqueConstraint("repository_id", "user_id", name="uq_repo_user_association"),
    )

    # ──────────────────── Relationships ──────────────────────
    repository: Mapped["Repository"] = relationship(
        "Repository", back_populates="user_associations", lazy="selectin"
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="repository_associations", lazy="selectin"
    )

    # ─────────────────────── Magic ───────────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<RepositoryUserAssociation repo_id={self.repository_id} "
            f"user_id={self.user_id} role={self.role!r}>"
        )


RepositoryUserAssociation = RepositoryUserAssociationModel
