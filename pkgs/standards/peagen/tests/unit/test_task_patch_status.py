import pytest

from peagen.plugins.queues.in_memory_queue import InMemoryQueue


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

    async def noop(task):
        return None

    monkeypatch.setattr(gw, "_persist", noop)
    monkeypatch.setattr(gw, "_publish_event", noop)

    task_submit = gw.task_submit
    task_patch = gw.task_patch
    task_get = gw.task_get

    result = await task_submit(pool="p", payload={}, taskId=None)
    tid = result["taskId"]

    await task_patch(taskId=tid, changes={"status": "success"})
    patched = await task_get(tid)
    assert patched["status"] == "success"
