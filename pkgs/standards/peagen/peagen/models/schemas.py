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
    pending = "pending"
    dispatched = "dispatched"
    running = "running"
    success = "success"
    failed = "failed"
    cancelled = "cancelled"

# ────────────────────────────────────────────────────────────────────────
# POSTGRES ENUM  (single source of truth for every table + migration)
# ────────────────────────────────────────────────────────────────────────
status_enum = psql.ENUM(
    *(s.value for s in Status),            # "pending", "running", ...
    name="status",
    create_type=False,                     # ← **critical**: never emit CREATE TYPE
)


class Task(BaseModel):
    id: str = Field(default=str(uuid.uuid4()))
    pool: str
    payload: dict
    status: Status = Status.pending
    result: Optional[dict] = None
    deps: List[str] = Field(default_factory=list)
    edge_pred: str | None = None
    labels: List[str] = Field(default_factory=list)
    config_toml: str | None = None

    def get(self, key: str, default=None):
        """Dictionary-style access to Task fields."""
        return self.__dict__.get(key, default)


class Pool(BaseModel):
    name: str
    members: List[str] = Field(default_factory=list)


class User(BaseModel):
    username: str
    role: Role = Role.user
