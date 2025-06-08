import msgspec
import jsonschema
import pytest

from peagen.task_model import Task, Result, TaskKind
from peagen.schemas import TASK_V1_SCHEMA, RESULT_V1_SCHEMA


@pytest.mark.unit
def test_task_roundtrip_and_schema():
    task = Task(kind=TaskKind.RENDER, id="a1b2c3d4e5f6a7b8", payload={"x": 1})
    data_json = msgspec.json.encode(task)
    task2 = msgspec.json.decode(data_json, type=Task)
    assert task == task2

    data_mp = msgspec.msgpack.encode(task)
    task3 = msgspec.msgpack.decode(data_mp, type=Task)
    assert task == task3

    obj = msgspec.json.decode(data_json)
    jsonschema.validate(obj, TASK_V1_SCHEMA)


@pytest.mark.unit
def test_result_roundtrip_and_schema():
    result = Result(task_id="abc", status="ok", data={"score": 5})
    js = msgspec.json.encode(result)
    result2 = msgspec.json.decode(js, type=Result)
    assert result == result2

    mp = msgspec.msgpack.encode(result)
    result3 = msgspec.msgpack.decode(mp, type=Result)
    assert result == result3

    obj = msgspec.json.decode(js)
    jsonschema.validate(obj, RESULT_V1_SCHEMA)
