import pytest

from peagen.models import Task, TaskRun
from peagen.plugins.queues.in_memory_queue import InMemoryQueue

@pytest.mark.unit
@pytest.mark.asyncio
async def test_task_model_roundtrip():
    t = Task(
        pool="p",
        payload={},
        deps=["a"],
        edge_pred="e",
        labels=["l"],
        in_degree=2,
        config_toml="cfg",
    )
    dumped = t.model_dump_json()
    t2 = Task.model_validate_json(dumped)
    assert t2.deps == ["a"]
    assert t2.edge_pred == "e"
    assert t2.labels == ["l"]
    assert t2.in_degree == 2
    assert t2.config_toml == "cfg"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_taskrun_from_task():
    t = Task(pool="p", payload={}, deps=["a"], edge_pred="e", labels=["l"], in_degree=1, config_toml="c")
    tr = TaskRun.from_task(t)
    assert tr.deps == ["a"]
    assert tr.edge_pred == "e"
    assert tr.labels == ["l"]
    assert tr.in_degree == 1
    assert tr.config_toml == "c"


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
    async def noop(*_):
        return None

    monkeypatch.setattr(gw, "_persist", noop)
    monkeypatch.setattr(gw, "_publish_event", noop)

    task_submit = gw.task_submit
    task_get = gw.task_get

    result = await task_submit(
        pool="p",
        payload={},
        taskId=None,
        deps=["d"],
        edge_pred="ep",
        labels=["lab"],
        in_degree=0,
        config_toml="cfg",
    )
    tid = result["taskId"]
    stored = await task_get(tid)
    assert stored["deps"] == ["d"]
    assert stored["edge_pred"] == "ep"
    assert stored["labels"] == ["lab"]
    assert stored["in_degree"] == 0
    assert stored["config_toml"] == "cfg"
