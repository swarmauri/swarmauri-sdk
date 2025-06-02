import datetime as dt
from sqlalchemy import Column, String, JSON, TIMESTAMP, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from .models import Status  # reuse enum
from pydantic import BaseModel

Base = declarative_base()

class TaskRun(BaseModel, Base):
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
