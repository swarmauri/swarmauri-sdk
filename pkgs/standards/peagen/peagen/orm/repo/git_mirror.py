"""peagen.orm.git_mirror
=======================

SQLAlchemy model representing a local Git mirror.
"""

from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..base import BaseModel


class GitMirrorModel(BaseModel):
    """Record for a mirrored Git repository."""

    __tablename__ = "git_mirrors"

    repo_url: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    local_path: Mapped[str] = mapped_column(String, nullable=False)
    last_fetched: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (UniqueConstraint("repo_url", name="uq_gitmirror_url"),)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<GitMirror repo_url={self.repo_url!r} local_path={self.local_path!r}>"
