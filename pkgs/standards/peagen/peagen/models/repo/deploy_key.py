"""
peagen.models.repo.deploy_key
=============================

Represents an SSH deploy key assigned to a Repository.

Design Notes
------------
• Each key belongs to exactly **one Repository** (FK ➜ repositories.id).
• `name` is unique within its repository to avoid collision.
• `public_key` is stored in cleartext for handshake / fingerprint checks.
• `private_key` is optional (NULLable) – store only when Peagen needs
  to act as that key; otherwise rely on external secret stores.
• `read_only` flag mirrors GitHub/Gitea deploy-key semantics.
"""

from __future__ import annotations

import uuid
from sqlalchemy import String, Boolean, Text, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import BaseModel


class DeployKey(BaseModel):
    """
    SSH deploy key bound to a repository.
    """

    __tablename__ = "deploy_keys"

    # ──────────────────────── Columns ────────────────────────
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String, nullable=False, doc="Human-friendly identifier (e.g., 'worker-01-ro')"
    )
    public_key: Mapped[str] = mapped_column(Text, nullable=False)
    private_key: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Optional – leave NULL if the private part is stored in Vault/SecretsMgr",
    )
    read_only: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, doc="RO/RW permission flag"
    )

    # Name must be unique inside each repository
    __table_args__ = (
        UniqueConstraint("repository_id", "name", name="uq_deploykey_per_repo"),
    )

    # ──────────────────── Relationships ──────────────────────
    repository: Mapped["Repository"] = relationship(
        "Repository", back_populates="deploy_keys", lazy="selectin"
    )

    # ─────────────────────── Magic ───────────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        scope = "RO" if self.read_only else "RW"
        return f"<DeployKey repo={self.repository_id} name={self.name!r} {scope}>"
