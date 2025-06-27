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
# ruff: noqa: F821

from __future__ import annotations

import uuid
from sqlalchemy import JSON, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import BaseModel  # id, timestamps
from .status import Status
from ..task import Task


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
    task_payload: Mapped["TaskPayload"] = relationship("TaskPayload", lazy="selectin")  # noqa: F821

    pool: Mapped["Pool | None"] = relationship("Pool", lazy="selectin")  # noqa: F821

    worker: Mapped["Worker | None"] = relationship("Worker", lazy="selectin")  # noqa: F821

    user: Mapped["User | None"] = relationship("User", lazy="selectin")  # noqa: F821

    # join-rows
    relation_associations: Mapped[list["TaskRunTaskRelationAssociation"]] = (
        relationship(
            "TaskRunTaskRelationAssociation",
            back_populates="task_run",
            cascade="all, delete-orphan",
            lazy="selectin",
        )
    )  # noqa: F821

    # convenience list of TaskRelation objects
    relations: Mapped[list["TaskRelation"]] = relationship(
        "TaskRelation",
        secondary="task_run_task_relation_associations",
        viewonly=True,
        lazy="selectin",
    )  # noqa: F821

    # Evaluation pipeline
    eval_results: Mapped[list["EvalResult"]] = relationship(
        "EvalResult",
        back_populates="task_run",
        cascade="all, delete-orphan",
        lazy="selectin",
    )  # noqa: F821

    # ────────────────────── Magic ───────────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return f"<TaskRun id={self.id} status={self.status}>"

    # ------------------------------------------------------------------
    @classmethod
    def from_task(cls, task: "Task") -> "TaskRun":
        """Create a minimal TaskRun instance from a :class:`Task`."""

        tr = cls(
            id=uuid.UUID(task.id),
            task_payload_id=uuid.uuid4(),
            status=task.status,
            result=None,
        )

        # attach extra metadata for convenience
        tr.relations = list(task.relations)
        tr.edge_pred = task.edge_pred
        tr.labels = list(task.labels)
        tr.in_degree = task.in_degree
        tr.config_toml = task.config_toml
        tr.commit_hexsha = task.commit_hexsha
        tr.oids = task.oids
        return tr
