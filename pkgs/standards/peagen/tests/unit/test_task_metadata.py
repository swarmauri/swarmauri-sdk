import pytest

import uuid
import datetime

from peagen.orm import Base, TaskModel, TaskRunModel
from peagen.orm.status import Status
from peagen.schemas import TaskRead
from peagen.plugins.queues.in_memory_queue import InMemoryQueue


@pytest.mark.unit
def test_taskread_roundtrip_json():
    now = datetime.datetime.now(datetime.timezone.utc)
    t = TaskRead(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        git_reference_id=uuid.uuid4(),
        pool="p",
        payload={},
        status=Status.queued,
        note="",
        spec_hash="dummy",
        date_created=now,
        last_modified=now,
    )
    dumped = t.model_dump_json()
    restored = TaskRead.model_validate_json(dumped)
    assert restored == t


@pytest.mark.unit
@pytest.mark.asyncio
async def test_taskrun_from_task(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    import importlib
    import peagen.gateway as gw
    import peagen.gateway.db as db

    importlib.reload(gw)

    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    gw.Session = db.Session
    gw.Session = db.Session

    t = TaskModel(
        id=str(uuid.uuid4()),
        tenant_id=uuid.uuid4(),
        git_reference_id=None,
        pool="p",
        payload={},
        status=Status.queued,
        note="",
        spec_hash="dummy",
    )
    t.relations = ["a"]
    t.edge_pred = "e"
    t.labels = ["l"]
    t.in_degree = 1
    t.config_toml = "c"
    t.commit_hexsha = None
    t.oids = []

    tr = TaskRunModel.from_task(t)
    assert str(tr.id) == t.id
    assert tr.status == t.status


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

    import peagen.gateway.db as db

    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    gw.Session = db.Session
    import peagen.gateway.rpc.tasks as task_rpc

    task_submit = task_rpc.task_submit

    from peagen.schemas import TaskCreate

    task = TaskCreate(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        git_reference_id=uuid.uuid4(),
        pool="p",
        payload={},
        status=Status.queued,
        note="",
        spec_hash="dummy",
        last_modified=datetime.datetime.now(datetime.timezone.utc),
    )

    monkeypatch.setattr(gw, "_publish_task", noop)
    monkeypatch.setattr(task_rpc, "_publish_task", noop)
    result = await task_submit(task)
    tid = result["taskId"]
    from peagen.gateway.rpc.tasks import _load_task

    stored_obj = await _load_task(tid)
    stored = stored_obj.model_dump()
    assert str(stored["id"]) == tid
