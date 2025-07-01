import asyncio
import importlib
import uuid
import datetime
import json
import pytest
from peagen.plugins.queues.in_memory_queue import InMemoryQueue
from peagen.orm.schemas import TaskRead


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
        if hasattr(task, "status"):
            called["status"] = task.status
            called["id"] = task.id
        else:
            called["status"] = task.get("status")
            tid = task.get("id")
            called["id"] = uuid.UUID(tid) if isinstance(tid, str) else tid

    monkeypatch.setattr(gw, "_save_task", record_save)

    async def stub_fail_task(task, exc):
        if isinstance(task, dict):
            blob = task
        else:
            blob = task.model_dump()
        blob["status"] = gw.Status.failed
        await gw._save_task(blob)

    monkeypatch.setattr(gw, "_fail_task", stub_fail_task)

    async def empty_workers(_pool):
        return []

    monkeypatch.setattr(gw, "_live_workers_by_pool", empty_workers)

    await q.sadd("pools", "p")
    task = TaskRead(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        git_reference_id=uuid.uuid4(),
        pool="p",
        payload={"action": "demo"},
        status=gw.Status.queued,
        note="",
        spec_hash=uuid.uuid4().hex,
        labels={},
        date_created=datetime.datetime.now(datetime.timezone.utc),
        last_modified=datetime.datetime.now(datetime.timezone.utc),
    )
    blob = task.model_dump()
    blob["labels"] = []
    await q.rpush(f"{gw.READY_QUEUE}:p", json.dumps(blob, default=str))

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
