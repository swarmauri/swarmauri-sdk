import asyncio
import importlib
import uuid
import datetime
import httpx
import pytest
from peagen.plugins.queues.in_memory_queue import InMemoryQueue
from peagen.orm.schemas import TaskRead


@pytest.mark.unit
@pytest.mark.asyncio
async def test_scheduler_removes_bad_worker(monkeypatch):
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

    from peagen.transport.jsonrpc_schemas.worker import RegisterParams

    await gw.worker_register(
        RegisterParams(
            workerId="w1",
            pool="p",
            url="http://w1/rpc",
            advertises={},
            handlers=["demo"],
        )
    )

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

    class DummyClient:
        def __init__(self, *a, **kw):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def post(self, url, json):
            raise httpx.ConnectError("fail")

    monkeypatch.setattr(gw.httpx, "AsyncClient", DummyClient)

    with pytest.raises(asyncio.CancelledError):
        await gw.scheduler()

    assert not await q.exists("worker:w1")
