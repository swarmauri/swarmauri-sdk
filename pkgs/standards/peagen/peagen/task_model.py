"""Task and Result dataclasses for the Peagen queue fabric."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Set
from datetime import datetime, timezone

import msgspec


def ts_utc() -> str:
    """Return current UTC time in ISO-8601 format."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class TaskKind(str, Enum):
    """Enumeration of task types."""

    RENDER = "render"
    MUTATE = "mutate"
    EXECUTE = "execute"
    EVALUATE = "evaluate"


class Task(msgspec.Struct, frozen=True):
    """Canonical task message."""

    kind: TaskKind
    id: str
    payload: dict[str, Any]
    requires: Set[str] = msgspec.field(default_factory=set)
    attempts: int = 0
    created_at: str = msgspec.field(default_factory=ts_utc)
    schema_v: int = 1


class Result(msgspec.Struct, frozen=True):
    """Result produced by a task handler."""

    task_id: str
    status: Literal["ok", "error", "skip"]
    data: dict[str, Any]
    created_at: str = msgspec.field(default_factory=ts_utc)
    attempts: int = 1
