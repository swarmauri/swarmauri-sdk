from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Literal, Set
import time


def ts_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class TaskKind(str, Enum):
    RENDER = "render"
    MUTATE = "mutate"
    EXECUTE = "execute"
    EVALUATE = "evaluate"


@dataclass(slots=True)
class Task:
    kind: TaskKind
    id: str
    payload: dict[str, Any]
    requires: Set[str] = field(default_factory=set)
    attempts: int = 0
    created_at: str = field(default_factory=ts_utc)
    schema_v: int = 1

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Result:
    task_id: str
    status: Literal["ok", "error", "skip"]
    data: dict[str, Any]
    created_at: str = field(default_factory=ts_utc)
    attempts: int = 1

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
