"""
peagen.models.task.task_relation
================================

Tenant-scoped logical grouping or relationship label for TaskRuns.

Examples
--------
• "experiment-group-Δ"
• "nightly-benchmark"
• "release-2025-07-A"
"""

from __future__ import annotations

import uuid
from sqlalchemy import String, Text, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import BaseModel


class TaskRelation(BaseModel):
    """
    A named relation / tag that can be attached to many TaskRuns.
    """

    __tablename__ = "task_relations"

    # ─────────────────── Columns ──────────────────
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="Relation label, unique per tenant.",
    )

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_task_relation_per_tenant"),
    )

    # ───────────── Relationships ────────────────
    tenant: Mapped["Tenant"] = relationship("Tenant", lazy="selectin")

    task_associations: Mapped[list["TaskRunTaskRelationAssociation"]] = relationship(
        "TaskRunTaskRelationAssociation",
        back_populates="relation",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    task_runs: Mapped[list["TaskRun"]] = relationship(
        "TaskRun",
        secondary="task_run_task_relation_associations",
        viewonly=True,
        lazy="selectin",
    )

    # ─────────────────── Magic ───────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return f"<TaskRelation id={self.id} tenant={self.tenant_id} name={self.name!r}>"
