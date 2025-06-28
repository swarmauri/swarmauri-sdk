import json
import importlib
import pytest

from peagen.plugins.queues.in_memory_queue import InMemoryQueue
from peagen.protocols.methods.worker import RegisterParams


@pytest.mark.unit
@pytest.mark.asyncio
async def test_worker_register_fetches_well_known(monkeypatch):
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

    async def fake_get(self, url):
        class R:
            status_code = 200

            def json(self):
                return {"handlers": ["a", "b"]}

        return R()

    class DummyClient:
        def __init__(self, *a, **kw):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get(self, url):
            return await fake_get(self, url)

    monkeypatch.setattr(gw.httpx, "AsyncClient", DummyClient)

    async def noop(*_args, **_kw):
        return None

    monkeypatch.setattr(gw, "_persist", noop)
    monkeypatch.setattr(gw, "_publish_event", noop)

    params = RegisterParams(workerId="w1", pool="p", url="http://w1/rpc", advertises={})
    await gw.worker_register(params)
    data = await q.hgetall("worker:w1")
    handlers = json.loads(data["handlers"])
    assert handlers == ["a", "b"]
