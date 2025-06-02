import datetime as dt
from sqlalchemy import Column, String, JSON, TIMESTAMP, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from .models import Status  # reuse enum

Base = declarative_base()

class TaskRun(Base):
    __tablename__ = "task_runs"

    id           = Column(UUID(as_uuid=True), primary_key=True)
    pool         = Column(String)
    task_type    = Column(String)
    status       = Column(Enum(Status))
    payload      = Column(JSON)
    result       = Column(JSON, nullable=True)
    artifact_uri = Column(String, nullable=True)
    started_at   = Column(TIMESTAMP(timezone=True), default=dt.datetime.utcnow)
    finished_at  = Column(TIMESTAMP(timezone=True), nullable=True)

    @classmethod
    def from_task(cls, task):
        return cls(
            id=task.id,
            pool=task.pool,
            task_type=task.payload.get("kind", "unknown"),
            status=task.status,
            payload=task.payload,
            result=task.result,
            artifact_uri=task.result.get("artifact") if task.result else None,
            finished_at=dt.datetime.utcnow()
            if task.status in {Status.success, Status.failed, Status.cancelled}
            else None,
        )

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
            "artifact_uri": self.artifact_uri,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }
        return {k: v for k, v in data.items() if k not in exclude}