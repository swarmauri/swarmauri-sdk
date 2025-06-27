"""
peagen.models.task.task_run
===========================

Execution record for a Task dispatched to the worker pool.

Relationships
-------------
Task       1 ─⟶ 1..n TaskRun
TaskRun      n ─⟶ n TaskRunDependencyAssociation (DAG edges)
TaskRun      1 ─⟶ 0..n EvalResult
"""

from __future__ import annotations

import uuid
from sqlalchemy import JSON, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - imports for type hints
    from ..infra.pool import Pool
    from ..infra.worker import Worker
    from ..tenant.user import User
    from .task import Task
    from .task_relation import TaskRelation
    from .task_run_relation_association import TaskRunTaskRelationAssociation
    from ..result.eval_result import EvalResult

from ..base import BaseModel  # id, timestamps
from .status import Status


class TaskRun(BaseModel):
    """
    One execution attempt of a Task on a Worker.
    """

    __tablename__ = "task_runs"

    # ─────────────────────── Columns ────────────────────────
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
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

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
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
    task: Mapped["Task"] = relationship("Task", lazy="selectin")

    pool: Mapped["Pool | None"] = relationship("Pool", lazy="selectin")

    worker: Mapped["Worker | None"] = relationship("Worker", lazy="selectin")

    user: Mapped["User | None"] = relationship("User", lazy="selectin")

    # join-rows
    relation_associations: Mapped[list["TaskRunTaskRelationAssociation"]] = (
        relationship(
            "TaskRunTaskRelationAssociation",
            back_populates="task_run",
            cascade="all, delete-orphan",
            lazy="selectin",
        )
    )

    # convenience list of TaskRelation objects
    relations: Mapped[list["TaskRelation"]] = relationship(
        "TaskRelation",
        secondary="task_run_task_relation_associations",
        viewonly=True,
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
