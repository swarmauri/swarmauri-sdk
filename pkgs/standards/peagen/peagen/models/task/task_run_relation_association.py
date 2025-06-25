"""
peagen.models.task.task_run_task_relation_association
=====================================================

Join table: links TaskRun ⇄ TaskRelation (many-to-many).
"""

from __future__ import annotations

import uuid
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import BaseModel


class TaskRunTaskRelationAssociation(BaseModel):
    __tablename__ = "task_run_task_relation_associations"

    # ─────────────────── Columns ──────────────────
    task_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("task_runs.id", ondelete="CASCADE"),
        nullable=False,
    )

    relation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("task_relations.id", ondelete="CASCADE"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("task_run_id", "relation_id", name="uq_task_run_relation"),
    )

    # ───────────── Relationships ────────────────
    task_run: Mapped["TaskRun"] = relationship(
        "TaskRun", back_populates="relation_associations", lazy="selectin"
    )
    relation: Mapped["TaskRelation"] = relationship(
        "TaskRelation", back_populates="task_associations", lazy="selectin"
    )

    # ─────────────────── Magic ───────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return f"<TaskRunTaskRelationAssociation run={self.task_run_id} rel={self.relation_id}>"
