"""
peagen.orm.task.task_run
===========================

Execution record for a Task dispatched to the worker pool.

Relationships
-------------
Task       1 ─⟶ 1..n TaskRun
TaskRun      n ─⟶ n TaskRunDependencyAssociation (DAG edges)
TaskRun      1 ─⟶ 0..n EvalResult
"""
# ruff: noqa: F821

from __future__ import annotations

import uuid
from sqlalchemy import JSON, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - imports for type hints
    from ..infra.pool import PoolModel
    from ..infra.worker import WorkerModel
    from ..tenant.user import UserModel
    from .task import TaskModel
    from .task_relation import TaskRelationModel
    from .task_run_relation_association import TaskRunTaskRelationAssociationModel
    from ..result.eval_result import EvalResultModel

from ..base import BaseModel  # id, timestamps
from .status import Status
from ..task.task import TaskModel
from ..infra.pool import PoolModel
from ..infra.worker import WorkerModel
from ..tenant.user import UserModel


class TaskRunModel(BaseModel):
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
    task: Mapped["TaskModel"] = relationship("TaskModel", lazy="selectin")

    pool: Mapped[PoolModel | None] = relationship("PoolModel", lazy="selectin")  # noqa: F821

    worker: Mapped[WorkerModel | None] = relationship("WorkerModel", lazy="selectin")  # noqa: F821

    user: Mapped[UserModel | None] = relationship("UserModel", lazy="selectin")  # noqa: F821

    # join-rows
    relation_associations: Mapped[list["TaskRunTaskRelationAssociationModel"]] = (
        relationship(
            "TaskRunTaskRelationAssociationModel",
            back_populates="task_run",
            cascade="all, delete-orphan",
            lazy="selectin",
        )
    )  # noqa: F821

    # convenience list of TaskRelation objects
    relations: Mapped[list["TaskRelationModel"]] = relationship(
        "TaskRelationModel",
        secondary="task_run_task_relation_associations",
        viewonly=True,
        lazy="selectin",
    )  # noqa: F821

    # Evaluation pipeline
    eval_results: Mapped[list["EvalResultModel"]] = relationship(
        "EvalResultModel",
        back_populates="task_run",
        cascade="all, delete-orphan",
        lazy="selectin",
    )  # noqa: F821

    # ────────────────────── Magic ───────────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return f"<TaskRun id={self.id} status={self.status}>"

    # ------------------------------------------------------------------
    @classmethod
    def from_task(cls, task: "TaskModel") -> "TaskRunModel":
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


TaskRun = TaskRunModel
