"""
peagen.orm.repo.git_reference
================================

Represents a single Git reference (branch, tag, or detached SHA)
belonging to a Repository.

Key Design
----------
• Scoped to one Repository (FK -> repositories.id).
• Uniqueness: reference name is unique per repository.
"""

from __future__ import annotations

import uuid
from sqlalchemy import String, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - imports for type hints
    from .repository import RepositoryModel

from ..base import BaseModel


class GitReferenceModel(BaseModel):
    """
    A named pointer within a Git repository (e.g., `refs/heads/main`).

    Columns
    -------
    repository_id : UUID      – owning repository
    name          : str       – fully-qualified ref (e.g., 'refs/heads/feature-x')
    commit_sha    : str       – 40-char SHA at the time Peagen recorded it
    remote_name   : str       – which remote this ref belongs to ('origin', 'upstream', …)
    """

    __tablename__ = "git_references"

    # ──────────────────────── Columns ────────────────────────
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    commit_sha: Mapped[str] = mapped_column(String(length=40), nullable=True)
    remote_name: Mapped[str] = mapped_column(String, nullable=False, default="origin")

    # Uniqueness: a repository cannot have two refs with the same name
    __table_args__ = (
        UniqueConstraint("repository_id", "name", name="uq_ref_per_repo"),
    )

    # ──────────────────── Relationships ──────────────────────
    repository: Mapped["RepositoryModel"] = relationship(
        "RepositoryModel",
        back_populates="git_references",
        lazy="selectin",
    )

    # ─────────────────────── Magic ───────────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<GitReference repo_id={self.repository_id} "
            f"name={self.name!r} sha={self.commit_sha or '…'}>"
        )


GitReference = GitReferenceModel
