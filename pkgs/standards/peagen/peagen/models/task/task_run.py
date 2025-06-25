"""
peagen.models.task.task_run
===========================

Execution record for a TaskPayload dispatched to the worker pool.

Relationships
-------------
TaskPayload 1 ─⟶ 1..n TaskRun
TaskRun      n ─⟶ n TaskRunDependencyAssociation (DAG edges)
TaskRun      1 ─⟶ 0..n EvalResult
"""

from __future__ import annotations

import uuid
from sqlalchemy import JSON, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import BaseModel  # id, timestamps
from .status import Status


class TaskRun(BaseModel):
    """
    One execution attempt of a TaskPayload on a Worker.
    """

    __tablename__ = "task_runs"

    # ─────────────────────── Columns ────────────────────────
    task_payload_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("task_payloads.id", ondelete="CASCADE"),
        nullable=False,
    )

    pool_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pools.id", ondelete="SET NULL"),
        nullable=True,
    )

    worker_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workers.id", ondelete="SET NULL"),
        nullable=True,
    )

    status: Mapped[Status] = mapped_column(
        Enum(Status, name="task_status_enum"),
        nullable=False,
        default=Status.queued,
    )

    result: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        doc="Arbitrary result JSON produced by the worker",
    )

    # ────────────────── Relationships ───────────────────────
    task_payload: Mapped["TaskPayload"] = relationship("TaskPayload", lazy="selectin")

    pool: Mapped["Pool | None"] = relationship("Pool", lazy="selectin")

    worker: Mapped["Worker | None"] = relationship("Worker", lazy="selectin")

    # DAG dependencies
    dependencies: Mapped[list["TaskRun"]] = relationship(
        "TaskRun",
        secondary="task_run_dependency_associations",
        primaryjoin="TaskRun.id==TaskRunDependencyAssociation.child_id",
        secondaryjoin="TaskRun.id==TaskRunDependencyAssociation.parent_id",
        lazy="selectin",
    )

    # Evaluation pipeline
    eval_results: Mapped[list["EvalResult"]] = relationship(
        "EvalResult",
        back_populates="task_run",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # ────────────────────── Magic ───────────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return f"<TaskRun id={self.id} status={self.status}>"


class TaskRunDep(BaseModel):
    """Association table capturing simple task run dependencies."""

    __tablename__ = "task_run_deps"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("task_runs.id", ondelete="CASCADE"),
        primary_key=True,
    )
    dep_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("task_runs.id", ondelete="CASCADE"),
        primary_key=True,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<TaskRunDep {self.task_id} depends_on {self.dep_id}>"
