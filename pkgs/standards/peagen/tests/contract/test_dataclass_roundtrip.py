import pytest
from dataclasses import dataclass, field
from enum import Enum


class TaskKind(str, Enum):
    RENDER = "render"
    MUTATE = "mutate"
    EXECUTE = "execute"
    EVALUATE = "evaluate"


@dataclass(slots=True)
class Task:
    kind: TaskKind
    id: str
    payload: dict[str, object]
    requires: set[str] = field(default_factory=set)
    attempts: int = 0
    created_at: str = "1970-01-01T00:00:00Z"
    schema_v: int = 1


@dataclass(slots=True)
class Result:
    task_id: str
    status: str
    data: dict[str, object]
    created_at: str = "1970-01-01T00:00:00Z"
    attempts: int = 1


@pytest.mark.unit
def test_task_round_trip_messagepack():
    msgspec = pytest.importorskip("msgspec")
    task = Task(TaskKind.RENDER, "1", {"a": 1}, {"cpu"})
    encoded = msgspec.msgpack.encode(task)
    decoded = msgspec.msgpack.decode(encoded, type=Task)
    assert decoded == task
    assert decoded.schema_v == task.schema_v


@pytest.mark.unit
def test_result_round_trip_messagepack():
    msgspec = pytest.importorskip("msgspec")
    result = Result("1", "ok", {"b": 2})
    encoded = msgspec.msgpack.encode(result)
    decoded = msgspec.msgpack.decode(encoded, type=Result)
    assert decoded == result
    assert decoded.attempts == result.attempts
