from __future__ import annotations
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


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
    id: str
    pool: str
    payload: dict
    status: Status = Status.pending
    result: Optional[dict] = None

    def get(self, key: str, default=None):
        """Dictionary-style access helper used by some handlers."""
        return getattr(self, key, default)


class Pool(BaseModel):
    name: str
    members: List[str] = Field(default_factory=list)


class User(BaseModel):
    username: str
    role: Role = Role.user
