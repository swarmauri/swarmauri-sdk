import msgspec
import jsonschema
import pytest

from peagen.task_model import (
    Task,
    Result,
    TaskKind,
    task_from_msgpack,
    task_to_msgpack,
)
from peagen.schemas import TASK_V1_SCHEMA, RESULT_V1_SCHEMA


@pytest.mark.unit
def test_task_roundtrip_and_schema():
    task = Task(kind=TaskKind.RENDER, id="a1b2c3d4e5f6a7b8", payload={"x": 1})
    data_json = msgspec.json.encode(task)
    task2 = msgspec.json.decode(data_json, type=Task)
    assert task == task2

    data_mp = task_to_msgpack(task)
    task3 = task_from_msgpack(data_mp)
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


@pytest.mark.unit
def test_unknown_fields_and_version_check():
    task = Task(TaskKind.EXECUTE, "t42", {})
    js = msgspec.json.encode(task)
    obj = msgspec.json.decode(js)
    obj["extra"] = 123
    js_extra = msgspec.json.encode(obj)
    assert msgspec.json.decode(js_extra, type=Task) == task

    obj["schema_v"] = task.schema_v + 1
    mp = msgspec.msgpack.encode(obj)
    with pytest.raises(ValueError):
        task_from_msgpack(mp)
