import pytest

from peagen.plugins.queues.in_memory_queue import InMemoryQueue


@pytest.mark.unit
@pytest.mark.asyncio
async def test_worker_list(monkeypatch):
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
    import peagen.gateway.rpc.workers as workers

    importlib.reload(gw)
    importlib.reload(workers)

    monkeypatch.setattr(gw, "queue", q)
    monkeypatch.setattr(gw, "result_backend", DummyBackend())
    monkeypatch.setattr(workers, "queue", q)

    async def noop(*_args, **_kw):
        return None

    monkeypatch.setattr(gw, "_persist", noop)
    monkeypatch.setattr(gw, "_publish_event", noop)

    from peagen.transport.json_rpcschemas.worker import RegisterParams, ListParams

    await gw.worker_register(
        RegisterParams(
            workerId="w1", pool="p", url="http://w1", advertises={}, handlers=["demo"]
        )
    )
    workers = await gw.worker_list(ListParams())
    assert workers[0]["id"] == "w1"
    assert workers[0]["pool"] == "p"
