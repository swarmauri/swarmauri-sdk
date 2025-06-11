import datetime as dt
from typing import Any, Dict, Iterable, Optional

from sqlalchemy import Column, String, JSON, TIMESTAMP, Enum
from sqlalchemy.dialects.postgresql import UUID, postgresql as psql
from sqlalchemy.orm import declarative_base

from peagen.models.schemas import Status

Base = declarative_base()

# ────────────────────────────────────────────────────────────────────────
# POSTGRES ENUM  (single source of truth for every table + migration)
# ────────────────────────────────────────────────────────────────────────
status_enum = psql.ENUM(
    *(s.value for s in Status),            # "pending", "running", ...
    name="status",
    create_type=False,                     # ← **critical**: never emit CREATE TYPE
)


class TaskRun(Base):
    __tablename__ = "task_runs"

    id           = Column(UUID(as_uuid=True), primary_key=True)
    pool         = Column(String)
    task_type    = Column(String)
    status       = Column(status_enum, nullable=False, default=Status.pending.value)
    payload      = Column(JSON)
    result       = Column(JSON, nullable=True)
    deps         = Column(JSON, nullable=False, default=list)
    edge_pred    = Column(String, nullable=True)
    labels       = Column(JSON, nullable=False, default=list)
    config_toml  = Column(String, nullable=True)
    artifact_uri = Column(String, nullable=True)
    started_at   = Column(TIMESTAMP(timezone=True), default=dt.datetime.utcnow)
    finished_at  = Column(TIMESTAMP(timezone=True), nullable=True)

    # ──────────────────────────────────────────────────────────────
    @classmethod
    def from_task(cls, task) -> "TaskRun":
        """Factory: build a TaskRun row from an in-memory Task object."""
        return cls(
            id=task.id,
            pool=task.pool,
            task_type=task.payload.get("kind", "unknown"),
            status=task.status,
            payload=task.payload,
            result=task.result,
            deps=task.deps,
            edge_pred=task.edge_pred,
            labels=task.labels,
            config_toml=task.config_toml,
            artifact_uri=(
                task.result.get("artifact_uri")
                if task.result and isinstance(task.result, dict)
                else None
            ),
            finished_at=dt.datetime.utcnow()
            if task.status in {Status.success, Status.failed, Status.cancelled}
            else None,
        )

    # ──────────────────────────────────────────────────────────────
    def to_dict(self, *, exclude: Optional[Iterable[str]] = None) -> Dict[str, Any]:
        """
        Convert this SQLAlchemy row into a plain dict.

        Parameters
        ----------
        exclude : Iterable[str], optional
            Column names to omit (e.g., {"id"} when doing an ON CONFLICT UPDATE).

        Returns
        -------
        dict
            Serializable mapping of column names → values.
        """
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
            "config_toml": self.config_toml,
            "artifact_uri": self.artifact_uri,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }
        return {k: v for k, v in data.items() if k not in exclude}
