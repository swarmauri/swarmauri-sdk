import pytest
import uuid
from datetime import datetime, timezone

from peagen.plugins.queues.in_memory_queue import InMemoryQueue
from peagen.schemas import TaskCreate
from peagen.orm.status import Status


@pytest.mark.unit
@pytest.mark.asyncio
async def test_task_patch_updates_status(monkeypatch):
    """Ensure Task.patch modifies the task status."""
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

    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    gw.engine = engine
    gw.Session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    import peagen.gateway.rpc.tasks as tasks_mod

    tasks_mod.Session = gw.Session

    async with engine.begin() as conn:
        await conn.run_sync(gw.Base.metadata.create_all)

    task_submit = gw.task_submit
    task_patch = gw.task_patch
    task_get = gw.task_get

    dto = TaskCreate(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        git_reference_id=uuid.uuid4(),
        pool="p",
        payload={},
        status=Status.queued,
        note="",
        spec_hash="dummy",
        last_modified=datetime.now(timezone.utc),
    )

    result = await task_submit(dto)
    tid = result["taskId"]

    await task_patch(taskId=tid, changes={"status": "success"})
    patched = await task_get(tid)
    assert patched["status"] == "success"
