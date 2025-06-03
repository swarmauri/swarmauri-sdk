"""Task and Result dataclasses for the Peagen queue fabric."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Set
from datetime import datetime, timezone

import msgspec


SCHEMA_V = 1


def ts_utc() -> str:
    """Return current UTC time in ISO-8601 format."""
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


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
    schema_v: int = SCHEMA_V


class Result(msgspec.Struct, frozen=True):
    """Result produced by a task handler."""

    task_id: str
    status: Literal["ok", "error", "skip"]
    data: dict[str, Any]
    created_at: str = msgspec.field(default_factory=ts_utc)
    attempts: int = 1


def _check_schema(version: int) -> None:
    if version > SCHEMA_V:
        raise ValueError(f"unsupported schema_v {version} > {SCHEMA_V}")


_msgpack_encoder = msgspec.msgpack.Encoder()
_task_msgpack_decoder = msgspec.msgpack.Decoder(Task, strict=False)
_result_msgpack_decoder = msgspec.msgpack.Decoder(Result, strict=False)


def task_to_msgpack(task: Task) -> bytes:
    return _msgpack_encoder.encode(task)


def task_from_msgpack(data: bytes) -> Task:
    task = _task_msgpack_decoder.decode(data)
    _check_schema(task.schema_v)
    return task


def result_to_msgpack(result: Result) -> bytes:
    return _msgpack_encoder.encode(result)


def result_from_msgpack(data: bytes) -> Result:
    return _result_msgpack_decoder.decode(data)


__all__ = [
    "SCHEMA_V",
    "ts_utc",
    "TaskKind",
    "Task",
    "Result",
    "task_to_msgpack",
    "task_from_msgpack",
    "result_to_msgpack",
    "result_from_msgpack",
]
