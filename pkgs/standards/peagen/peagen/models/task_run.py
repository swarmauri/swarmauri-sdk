import datetime as dt
import uuid
from typing import Any, Dict, Iterable, Optional, List

from sqlalchemy import JSON, TIMESTAMP, String, Column, ForeignKey
from sqlalchemy.dialects import postgresql as psql
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from peagen.models.schemas import Status


class Base(DeclarativeBase):
    pass


# ────────────────────────────────────────────────────────────────────────
# POSTGRES ENUM  (single source of truth for every table + migration)
# ────────────────────────────────────────────────────────────────────────
status_enum = psql.ENUM(
    *(s.value for s in Status),
    name="status",
    create_type=False,
)


class TaskRunDep(Base):
    __tablename__ = "task_run_deps"

    task_id = Column(UUID(as_uuid=True), ForeignKey("task_runs.id"), primary_key=True)
    dep_id = Column(UUID(as_uuid=True), ForeignKey("task_runs.id"), primary_key=True)


class TaskRun(Base):
    __tablename__ = "task_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    pool: Mapped[str | None] = mapped_column(String)
    task_type: Mapped[str | None] = mapped_column(String)
    status: Mapped[str] = mapped_column(
        status_enum, nullable=False, default=Status.waiting.value
    )
    payload: Mapped[dict | None] = mapped_column(JSON)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    deps: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    edge_pred: Mapped[str | None] = mapped_column(String, nullable=True)
    labels: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    in_degree: Mapped[int] = mapped_column(psql.INTEGER, nullable=False, default=0)
    config_toml: Mapped[str | None] = mapped_column(String, nullable=True)
    artifact_uri: Mapped[str | None] = mapped_column(String, nullable=True)
    commit_hexsha: Mapped[str | None] = mapped_column(String, nullable=True)
    started_at: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=dt.datetime.utcnow
    )
    finished_at: Mapped[dt.datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    _deps_rel = relationship(
        "TaskRun",
        secondary="task_run_deps",
        primaryjoin=id == TaskRunDep.task_id,
        secondaryjoin=id == TaskRunDep.dep_id,
        lazy="selectin",
    )

    def __init__(self, **kwargs) -> None:
        self._raw_deps: List[str] = kwargs.pop("deps", [])
        super().__init__(**kwargs)

    @property
    def deps(self) -> List[str]:  # noqa: F811 - overrides the mapped column
        if getattr(self, "_raw_deps", None):
            return self._raw_deps
        return [str(d.id) for d in self._deps_rel]
    # ──────────────────────────────────────────────────────────────
    @classmethod
    def from_task(cls, task) -> "TaskRun":
        """Factory: build a TaskRun row from an in-memory Task object."""
        tr = cls(
            id=task.id,
            pool=task.pool,
            task_type=task.payload.get("kind", "unknown"),
            status=task.status,
            payload=task.payload,
            result=task.result,
            edge_pred=task.edge_pred,
            labels=task.labels,
            in_degree=task.in_degree,
            config_toml=task.config_toml,
            oids=(
                task.result.get("oids")
                if task.result and isinstance(task.result, dict)
                else None
            ),
            commit_hexsha=(
                task.result.get("commit")
                if task.result and isinstance(task.result, dict)
                else None
            ),
            started_at=(
                dt.datetime.utcfromtimestamp(task.started_at)
                if task.started_at
                else dt.datetime.utcnow()
            ),
            finished_at=dt.datetime.utcnow()
            if task.status in {Status.success, Status.failed, Status.cancelled}
            else None,
        )
        tr._raw_deps = list(task.deps)
        return tr

    # ──────────────────────────────────────────────────────────────
    def to_dict(self, *, exclude: Optional[Iterable[str]] = None) -> Dict[str, Any]:
        """Convert this SQLAlchemy row into a plain dict."""
        exclude = set(exclude or ())
        data = {
            "id": self.id,
            "pool": self.pool,
            "task_type": self.task_type,
            "status": self.status,
            "payload": self.payload,
            "result": self.result,
            "deps": self.deps,
            "edge_pred": self.edge_pred,
            "labels": self.labels,
            "in_degree": self.in_degree,
            "config_toml": self.config_toml,
            "oids": self.oids,
            "commit_hexsha": self.commit_hexsha,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration": (
                int((self.finished_at - self.started_at).total_seconds())
                if self.started_at and self.finished_at
                else None
            ),
        }
        return {k: v for k, v in data.items() if k not in exclude}
