from __future__ import annotations
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid




class Role(str, Enum):
    admin = "admin"
    user = "user"
    worker = "worker"


class Status(str, Enum):
    """Enumeration of task states."""

    queued = "queued"
    waiting = "waiting"
    input_required = "input_required"
    auth_required = "auth_required"
    approved = "approved"
    rejected = "rejected"
    dispatched = "dispatched"
    running = "running"
    paused = "paused"
    success = "success"
    failed = "failed"
    cancelled = "cancelled"


class Task(BaseModel):
    id: str = Field(default=str(uuid.uuid4()))
    pool: str
    payload: dict
    status: Status = Status.waiting
    result: Optional[dict] = None
    deps: List[str] = Field(default_factory=list)
    edge_pred: str | None = None
    labels: List[str] = Field(default_factory=list)
    in_degree: int = 0
    config_toml: str | None = None
    started_at: float | None = None
    finished_at: float | None = None
    lock_hash: str | None = None
    chain_hash: str | None = None

    @property
    def duration(self) -> int | None:
        """Return runtime in seconds if start and end are known."""
        if self.started_at is None or self.finished_at is None:
            return None
        return int(self.finished_at - self.started_at)

    def get(self, key: str, default=None):
        """Dictionary-style access to Task fields."""
        return self.__dict__.get(key, default)


class Pool(BaseModel):
    name: str
    members: List[str] = Field(default_factory=list)


class User(BaseModel):
    username: str
    role: Role = Role.user
