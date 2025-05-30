from __future__ import annotations
from dataclasses import dataclass, field
import pytest

msgspec = pytest.importorskip("msgspec")


@dataclass(slots=True)
class Task:
    kind: str
    id: str
    payload: dict[str, str]
    requires: set[str] = field(default_factory=set)
    attempts: int = 0
    created_at: str = "2024-01-01T00:00:00Z"
    schema_v: int = 1


@dataclass(slots=True)
class Result:
    task_id: str
    status: str
    data: dict[str, int]
    created_at: str = "2024-01-01T00:00:00Z"
    attempts: int = 1


TASK_MSGPACK = bytes.fromhex(
    "87a46b696e64a66d7574617465a26964a3313233a77061796c6f616481a474657874"
    "a568656c6c6fa8726571756972657390a8617474656d70747300aa637265617465645f"
    "6174b4323032342d30312d30315430303a30303a30305aa8736368656d615f7601"
)


RESULT_MSGPACK = bytes.fromhex(
    "7461736b5f69643132337374617475736f6b64617461726573756c742a6372656174"
    "65645f6174323032342d30312d30315430303a30303a30305a617474656d70747301"
)


@pytest.mark.unit
def test_task_roundtrip():
    task = Task(kind="mutate", id="123", payload={"text": "hello"})
    packed = msgspec.msgpack.encode(task)
    assert packed == TASK_MSGPACK

    decoded = msgspec.msgpack.decode(packed, type=Task)
    assert decoded == task
    assert decoded.schema_v == 1


@pytest.mark.unit
def test_result_roundtrip():
    result = Result(task_id="123", status="ok", data={"result": 42})
    packed = msgspec.msgpack.encode(result)
    assert packed == RESULT_MSGPACK

    decoded = msgspec.msgpack.decode(packed, type=Result)
    assert decoded == result
