import importlib
import pytest

from peagen.plugins.queues.in_memory_queue import InMemoryQueue
from peagen.protocols.methods.worker import RegisterParams


@pytest.mark.unit
@pytest.mark.asyncio
async def test_worker_register_rejects_no_handlers(monkeypatch):
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
    monkeypatch.setattr(gw, "_publish_event", noop)

    with pytest.raises(gw.RPCException) as exc:
        params = RegisterParams(
            workerId="w1",
            pool="p",
            url="http://w1/rpc",
            advertises={},
            handlers=[],
        )
        await gw.worker_register(params)
    assert exc.value.code == -32602
    data = await q.hgetall("worker:w1")
    assert data == {}
