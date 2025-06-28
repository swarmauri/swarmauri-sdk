import datetime
import uuid

import pytest

from peagen.orm import TaskModel, TaskRunModel, Status
from peagen.schemas import TaskCreate, TaskRead
from peagen.plugins.queues.in_memory_queue import InMemoryQueue


@pytest.mark.unit
@pytest.mark.asyncio
async def test_task_model_roundtrip():
    t = TaskRead(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        git_reference_id=uuid.uuid4(),
        pool="p",
        payload={},
        status=Status.queued,
        note="",
        spec_hash=uuid.uuid4().hex,
        date_created=datetime.datetime.now(datetime.timezone.utc),
        last_modified=datetime.datetime.now(datetime.timezone.utc),
    )
    dumped = t.model_dump_json()
    t2 = TaskRead.model_validate_json(dumped)
    assert t2 == t


@pytest.mark.unit
@pytest.mark.asyncio
async def test_taskrun_from_task():
    t = TaskModel(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        pool="p",
        payload={},
        spec_hash=uuid.uuid4().hex,
        status=Status.queued,
    )
    tr = TaskRunModel.from_task(t)
    assert tr.id == uuid.UUID(str(t.id))
    assert tr.status == Status.queued


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
    task_get = gw.task_get

    dto = TaskCreate(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        git_reference_id=uuid.uuid4(),
        pool="p",
        payload={},
        status=Status.queued,
        note="",
        spec_hash=uuid.uuid4().hex,
        last_modified=datetime.datetime.now(datetime.timezone.utc),
    )

    result = await task_submit(dto)
    tid = result["taskId"]
    from peagen.protocols.methods.task import GetParams

    stored = await task_get(GetParams(taskId=tid))
    assert stored["pool"] == "p"
    assert stored["payload"] == {}
