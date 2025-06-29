import uuid
import pytest
from peagen.plugins.queues.in_memory_queue import InMemoryQueue


@pytest.mark.unit
@pytest.mark.asyncio
async def test_task_patch_triggers_finalize(monkeypatch):
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

    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    gw.engine = engine
    gw.Session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    import peagen.gateway.rpc.tasks as tasks_mod

    tasks_mod.Session = gw.Session

    async with engine.begin() as conn:
        await conn.run_sync(gw.Base.metadata.create_all)

    async def noop(*_args, **_kwargs):
        return None

    monkeypatch.setattr(gw, "_persist", noop)
    monkeypatch.setattr(gw, "_publish_event", noop)

    task_submit = gw.task_submit
    task_patch = gw.task_patch
    task_get = gw.task_get
    work_finished = gw.work_finished

    from peagen.schemas import TaskCreate
    from peagen.orm.status import Status
    import datetime
    from datetime import timezone

    parent_dto = TaskCreate(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        git_reference_id=uuid.uuid4(),
        pool="p",
        payload={},
        status=Status.queued,
        note="",
        spec_hash=uuid.uuid4().hex,
        last_modified=datetime.datetime.now(timezone.utc),
    )
    parent_id = (await task_submit(parent_dto)).taskId

    child_dto = TaskCreate(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        git_reference_id=uuid.uuid4(),
        pool="p",
        payload={},
        status=Status.queued,
        note="",
        spec_hash=uuid.uuid4().hex,
        last_modified=datetime.datetime.now(timezone.utc),
    )
    child_id = (await task_submit(child_dto)).taskId
    await work_finished(taskId=child_id, status="success", result=None)

    await task_patch(taskId=parent_id, changes={"result": {"children": [child_id]}})
    parent = await task_get(parent_id)
    assert parent.status == "success"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_task_patch_triggers_finalize_rejected(monkeypatch):
    """Finalize parent when child task is rejected."""
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

    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    gw.engine = engine
    gw.Session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    import peagen.gateway.rpc.tasks as tasks_mod

    tasks_mod.Session = gw.Session

    async with engine.begin() as conn:
        await conn.run_sync(gw.Base.metadata.create_all)

    async def noop(*_args, **_kwargs):
        return None

    monkeypatch.setattr(gw, "_persist", noop)
    monkeypatch.setattr(gw, "_publish_event", noop)

    task_submit = gw.task_submit
    task_patch = gw.task_patch
    task_get = gw.task_get
    work_finished = gw.work_finished

    from peagen.schemas import TaskCreate
    from peagen.orm.status import Status
    import datetime
    from datetime import timezone

    parent_dto = TaskCreate(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        git_reference_id=uuid.uuid4(),
        pool="p",
        payload={},
        status=Status.queued,
        note="",
        spec_hash=uuid.uuid4().hex,
        last_modified=datetime.datetime.now(timezone.utc),
    )
    parent_id = (await task_submit(parent_dto)).taskId

    child_dto = TaskCreate(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        git_reference_id=uuid.uuid4(),
        pool="p",
        payload={},
        status=Status.queued,
        note="",
        spec_hash=uuid.uuid4().hex,
        last_modified=datetime.datetime.now(timezone.utc),
    )
    child_id = (await task_submit(child_dto)).taskId
    await work_finished(taskId=child_id, status="rejected", result=None)

    await task_patch(taskId=parent_id, changes={"result": {"children": [child_id]}})
    parent = await task_get(parent_id)
    assert parent.status == "success"
