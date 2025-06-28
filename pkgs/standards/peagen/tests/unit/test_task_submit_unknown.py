import importlib
import pytest

from peagen.plugins.queues.in_memory_queue import InMemoryQueue


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
    import peagen.gateway.rpc.tasks as tasks_mod

    monkeypatch.setattr(tasks_mod, "queue", q)

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

    from peagen.tui.task_submit import build_task

    dto = build_task("bar", {}, pool="p")
    with pytest.raises(gw.RPCException) as exc:
        await gw.task_submit(dto)
    assert exc.value.code == -32601
    items = await q.lrange("ready:p", 0, -1)
    assert items == []
