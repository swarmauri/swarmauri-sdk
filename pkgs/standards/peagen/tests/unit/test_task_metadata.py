import pytest

from peagen.models.task.task import Task
from peagen.models.task.task_run import TaskRun
from datetime import datetime, UTC
import uuid
from peagen.models.schemas import TaskCreate, TaskRead
from peagen.models.task.task import TaskModel
from peagen.plugins.queues.in_memory_queue import InMemoryQueue


@pytest.mark.unit
@pytest.mark.asyncio
async def test_task_model_roundtrip():
    t = Task(
        pool="p",
        payload={},
        relations=["a"],
        edge_pred="e",
        labels=["l"],
        in_degree=2,
        config_toml="cfg",
    )
    dumped = t.model_dump_json()
    t2 = Task.model_validate_json(dumped)
    assert t2.relations == ["a"]
    assert t2.edge_pred == "e"
    assert t2.labels == ["l"]
    assert t2.in_degree == 2
    assert t2.config_toml == "cfg"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_taskrun_from_task():
    t = Task(
        pool="p",
        payload={},
        relations=["a"],
        edge_pred="e",
        labels=["l"],
        in_degree=1,
        config_toml="c",
    )
    tr = TaskRun.from_task(t)
    assert tr.relations == ["a"]
    assert tr.edge_pred == "e"
    assert tr.labels == ["l"]
    assert tr.in_degree == 1
    assert tr.config_toml == "c"
    assert tr.commit_hexsha is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_task_submit_roundtrip(monkeypatch):
    q = InMemoryQueue()

    class DummyBackend:
        async def store(self, task_run):
            pass

    class StubPM:
        def __init__(self, cfg):
            pass

        def get(self, group):
            if group == "queues":
                return q
            if group == "result_backends":
                return DummyBackend()
            return None

    import importlib
    import peagen.plugins

    monkeypatch.setattr(peagen.plugins, "PluginManager", StubPM)
    import peagen.gateway as gw

    importlib.reload(gw)

    monkeypatch.setattr(gw, "queue", q)
    monkeypatch.setattr(gw, "result_backend", DummyBackend())

    async def noop(*_args, **_kwargs):
        return None

    monkeypatch.setattr(gw, "_persist", noop)
    monkeypatch.setattr(gw, "_publish_event", noop)

    task_submit = gw.task_submit
    task_get = gw.task_get

    result = await task_submit(
        pool="p",
        payload={},
        taskId=None,
        relations=["d"],
        edge_pred="ep",
        labels=["lab"],
        in_degree=0,
        config_toml="cfg",
    )
    tid = result["taskId"]
    stored = await task_get(tid)
    assert stored["relations"] == ["d"]
    assert stored["edge_pred"] == "ep"
    assert stored["labels"] == ["lab"]
    assert stored["in_degree"] == 0
    assert stored["config_toml"] == "cfg"


@pytest.mark.unit
def test_task_schema_roundtrip():
    now = datetime.now(UTC)
    create = TaskCreate(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        git_reference_id=uuid.uuid4(),
        parameters={"x": 1},
        note="demo",
    )
    model = TaskModel(
        date_created=now,
        last_modified=now,
        **create.model_dump(),
    )
    fields = TaskRead.model_fields.keys()
    read = TaskRead(**{f: getattr(model, f) for f in fields})
    dumped = read.model_dump_json()
    roundtrip = TaskRead.model_validate_json(dumped)
    assert roundtrip == read
