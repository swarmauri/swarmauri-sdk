"""
peagen.models.task.task_relation
================================

Defines a named relationship that can be attached to task runs.
"""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..base import BaseModel


class TaskRelation(BaseModel):
    """A reusable task relation definition."""

    __tablename__ = "task_relations"

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<TaskRelation name={self.name!r}>"
