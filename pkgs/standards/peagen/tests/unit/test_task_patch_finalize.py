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

    async def noop(*_args, **_kwargs):
        return None

    monkeypatch.setattr(gw, "_persist", noop)
    monkeypatch.setattr(gw, "_publish_event", noop)

    task_submit = gw.task_submit
    task_patch = gw.task_patch
    task_get = gw.task_get
    work_finished = gw.work_finished

    parent_id = (await task_submit(pool="p", payload={"action": "noop"}, taskId=None))[
        "taskId"
    ]
    child_id = str(uuid.uuid4())
    await task_submit(pool="p", payload={"action": "noop"}, taskId=child_id)
    await work_finished(taskId=child_id, status="success", result=None)

    await task_patch(taskId=parent_id, changes={"result": {"children": [child_id]}})
    parent = await task_get(parent_id)
    assert parent["status"] == "success"


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

    async def noop(*_args, **_kwargs):
        return None

    monkeypatch.setattr(gw, "_persist", noop)
    monkeypatch.setattr(gw, "_publish_event", noop)

    task_submit = gw.task_submit
    task_patch = gw.task_patch
    task_get = gw.task_get
    work_finished = gw.work_finished

    parent_id = (await task_submit(pool="p", payload={"action": "noop"}, taskId=None))[
        "taskId"
    ]
    child_id = str(uuid.uuid4())
    await task_submit(pool="p", payload={"action": "noop"}, taskId=child_id)
    await work_finished(taskId=child_id, status="rejected", result=None)

    await task_patch(taskId=parent_id, changes={"result": {"children": [child_id]}})
    parent = await task_get(parent_id)
    assert parent["status"] == "success"
