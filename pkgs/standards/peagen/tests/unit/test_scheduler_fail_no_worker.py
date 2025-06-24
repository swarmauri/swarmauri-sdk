import asyncio
import importlib
import pytest
from peagen.plugins.queues.in_memory_queue import InMemoryQueue


@pytest.mark.unit
@pytest.mark.asyncio
async def test_scheduler_fails_task_without_worker(monkeypatch):
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

    import peagen.plugins

    monkeypatch.setattr(peagen.plugins, "PluginManager", StubPM)
    import peagen.gateway as gw

    importlib.reload(gw)

    monkeypatch.setattr(gw, "queue", q)
    monkeypatch.setattr(gw, "result_backend", DummyBackend())

    async def noop(*_args, **_kw):
        return None

    monkeypatch.setattr(gw, "_persist", noop)
    monkeypatch.setattr(gw, "_publish_task", noop)

    called = {}

    async def record_save(task):
        called["status"] = task.status
        called["id"] = task.id

    monkeypatch.setattr(gw, "_save_task", record_save)

    async def empty_workers(_pool):
        return []

    monkeypatch.setattr(gw, "_live_workers_by_pool", empty_workers)

    await q.sadd("pools", "p")
    task = gw.Task(pool="p", payload={"action": "demo"})
    await q.rpush(f"{gw.READY_QUEUE}:p", task.model_dump_json())

    orig_blpop = q.blpop
    first = True

    async def fake_blpop(keys, timeout):
        nonlocal first
        if first:
            first = False
            return await orig_blpop(keys, timeout)
        raise asyncio.CancelledError

    monkeypatch.setattr(q, "blpop", fake_blpop)

    with pytest.raises(asyncio.CancelledError):
        await gw.scheduler()

    assert called.get("status") == gw.Status.failed
    assert called.get("id") == task.id
