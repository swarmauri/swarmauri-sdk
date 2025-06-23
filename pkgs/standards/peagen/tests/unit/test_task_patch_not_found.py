import pytest

from peagen.plugins.queues.in_memory_queue import InMemoryQueue


@pytest.mark.unit
@pytest.mark.asyncio
async def test_task_patch_missing(monkeypatch):
    """Verify ValueError raised when patching a nonexistent task."""
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

    task_patch = gw.task_patch

    with pytest.raises(ValueError):
        await task_patch(taskId="missing", changes={"status": "success"})
