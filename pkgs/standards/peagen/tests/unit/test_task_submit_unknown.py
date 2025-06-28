import importlib
import pytest

import uuid
from datetime import datetime, timezone

from peagen.plugins.queues.in_memory_queue import InMemoryQueue
from peagen.schemas import TaskCreate
from peagen.orm.status import Status


@pytest.mark.unit
@pytest.mark.asyncio
async def test_task_submit_unknown_action(monkeypatch):
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
    import peagen

    importlib.reload(gw)

    monkeypatch.setattr(gw, "queue", q)
    monkeypatch.setattr(gw, "result_backend", DummyBackend())

    async def noop(*_args, **_kw):
        return None

    monkeypatch.setattr(gw, "_persist", noop)
    monkeypatch.setattr(gw, "_publish_event", noop)

    await gw.worker_register(
        workerId="w1",
        pool="p",
        url="http://w1/rpc",
        advertises={},
        handlers=["foo"],
    )

    task = TaskCreate(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        git_reference_id=uuid.uuid4(),
        pool="p",
        payload={"action": "bar"},
        status=Status.queued,
        note="",
        spec_hash="dummy",
        last_modified=datetime.now(timezone.utc),
    )

    with pytest.raises(gw.RPCException) as exc:
        await gw.task_submit(pool="p", payload=task.payload)
    assert exc.value.code == -32601
    items = await q.lrange("ready:p", 0, -1)
    assert items == []
