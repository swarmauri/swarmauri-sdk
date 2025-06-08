from __future__ import annotations
from enum import Enum
from typing import Any, List, Optional
from pydantic import BaseModel, Field
import uuid


class Role(str, Enum):
    admin = "admin"
    user = "user"
    worker = "worker"


class Status(str, Enum):
    pending = "pending"
    dispatched = "dispatched"
    running = "running"
    success = "success"
    failed = "failed"
    cancelled = "cancelled"


class Task(BaseModel):
    id: str = Field(default=str(uuid.uuid4()))
    pool: str
    payload: dict
    deps: list[str] = Field(default_factory=list)
    edge_pred: str | None = None
    labels: list[str] = Field(default_factory=list)
    interface_args: dict[str, Any] = Field(default_factory=dict)
    config_toml: str = ""
    status: Status = Status.pending
    result: Optional[dict] = None

    def get(self, key: str, default=None):
        """Dictionary-style access to Task fields."""
        return self.__dict__.get(key, default)


class Pool(BaseModel):
    name: str
    members: List[str] = Field(default_factory=list)


class User(BaseModel):
    username: str
    role: Role = Role.user
