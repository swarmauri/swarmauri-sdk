import asyncio
import pytest

from peagen.plugins.queues.in_memory_queue import InMemoryQueue
from peagen.models import Task


@pytest.mark.unit
@pytest.mark.asyncio
async def test_task_submit_indexes_labels(monkeypatch):
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

    async def noop(*args, **kwargs):
        return None

    monkeypatch.setattr(gw, "_persist", noop)
    monkeypatch.setattr(gw, "_publish_event", noop)

    result = await gw.task_submit(pool="p", payload={}, taskId=None, labels=["lbl"])
    tid = result["taskId"]
    assert await q.smembers("label:lbl:tasks") == [tid]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_check_task_labels_paused(monkeypatch):
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

    async def noop(*args, **kwargs):
        return None

    monkeypatch.setattr(gw, "_persist", noop)
    monkeypatch.setattr(gw, "_publish_event", noop)

    await gw.label_pause("lbl")
    t = Task(pool="p", payload={}, labels=["lbl"])
    assert not await gw._check_task_labels(t)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_check_task_labels_rate_limit(monkeypatch):
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

    async def noop(*args, **kwargs):
        return None

    monkeypatch.setattr(gw, "_persist", noop)
    monkeypatch.setattr(gw, "_publish_event", noop)

    now = asyncio.get_event_loop().time()
    await gw.label_update("lbl", {"rate": "1", "allowed_after": str(now + 10)})
    t = Task(pool="p", payload={}, labels=["lbl"])
    assert not await gw._check_task_labels(t)
