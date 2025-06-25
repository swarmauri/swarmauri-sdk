"""
peagen.models.task.task_run_relation_association
================================================

Generic edge linking two TaskRun rows with an explicit *relation_type*.

RelationType examples
---------------------
• depends_on        – logical/temporal dependency  (old DAG edge)
• duplicate_of      – indicates the child duplicates parent results
• experiment_group  – groups runs under an experiment bucket
• supersedes        – child is an updated run superseding parent
Feel free to extend the Enum values as needs evolve.
"""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import Enum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import BaseModel


class RelationType(str, enum.Enum):
    depends_on = "depends_on"
    duplicate_of = "duplicate_of"
    experiment_group = "experiment_group"
    supersedes = "supersedes"


class TaskRunRelationAssociation(BaseModel):
    __tablename__ = "task_run_relation_associations"

    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("task_runs.id", ondelete="CASCADE"), nullable=False
    )
    child_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("task_runs.id", ondelete="CASCADE"), nullable=False
    )
    relation_type: Mapped[RelationType] = mapped_column(
        Enum(RelationType, name="taskrun_relation_type_enum"),
        nullable=False,
        default=RelationType.depends_on,
    )

    __table_args__ = (
        UniqueConstraint(
            "parent_id", "child_id", "relation_type", name="uq_taskrun_relation_edge"
        ),
    )

    # back-refs (optional view-only helpers)
    parent: Mapped["TaskRun"] = relationship(
        "TaskRun",
        foreign_keys=[parent_id],
        lazy="selectin",
        viewonly=True,
    )
    child: Mapped["TaskRun"] = relationship(
        "TaskRun",
        foreign_keys=[child_id],
        lazy="selectin",
        viewonly=True,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<TaskRunRelationAssociation {self.parent_id} → {self.child_id} "
            f"type={self.relation_type}>"
        )
