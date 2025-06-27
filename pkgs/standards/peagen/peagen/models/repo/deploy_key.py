"""
peagen.models.repo.deploy_key
=============================

Represents an SSH deploy key owned by a user. Keys may be attached to
multiple repositories via a join table.

Design Notes
------------
• Each key belongs to exactly **one User** (FK ➜ users.id).
• Keys can be attached to many repositories via
  RepositoryDeployKeyAssociation.
• `name` is unique per user to avoid collision.
• `public_key` is stored in cleartext for handshake / fingerprint checks.
• Private keys are stored as Secrets – we only reference the Secret ID.
• `read_only` flag mirrors GitHub/Gitea deploy-key semantics.
"""

from __future__ import annotations

import uuid
from sqlalchemy import String, Boolean, Text, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..tenant.user import User
    from ..secret.secret import Secret
    from .repository_deploy_key_association import RepositoryDeployKeyAssociation
    from .repository import Repository

from ..base import BaseModel


class DeployKey(BaseModel):
    """SSH deploy key bound to a user."""

    __tablename__ = "deploy_keys"

    # ──────────────────────── Columns ────────────────────────
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String, nullable=False, doc="Human-friendly identifier (e.g., 'worker-01-ro')"
    )
    public_key: Mapped[str] = mapped_column(Text, nullable=False)
    secret_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("secrets.id", ondelete="CASCADE"),
        nullable=False,
    )
    read_only: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, doc="RO/RW permission flag"
    )

    # Name must be unique per user
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_deploykey_per_user"),
    )

    # ──────────────────── Relationships ──────────────────────
    user: Mapped["User"] = relationship("User", lazy="selectin")
    secret: Mapped["Secret"] = relationship("Secret", lazy="selectin")

    repository_associations: Mapped[list["RepositoryDeployKeyAssociation"]] = (
        relationship(
            "RepositoryDeployKeyAssociation",
            back_populates="deploy_key",
            cascade="all, delete-orphan",
            lazy="selectin",
        )
    )

    repositories: Mapped[list["Repository"]] = relationship(
        "Repository",
        secondary="repository_deploy_key_associations",
        back_populates="deploy_keys",
        lazy="selectin",
    )

    # ─────────────────────── Magic ───────────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        scope = "RO" if self.read_only else "RW"
        return f"<DeployKey user={self.user_id} name={self.name!r} {scope}>"
