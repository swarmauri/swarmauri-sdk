import pytest
from peagen.plugins.queues.in_memory_queue import InMemoryQueue


@pytest.mark.unit
@pytest.mark.asyncio
async def test_task_submit_unknown_handler(monkeypatch):
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

    async def fake_live(pool):
        return []

    monkeypatch.setattr(gw, "_live_workers_by_pool", fake_live)

    counts = {}

    async def fake_record(session, ip):
        counts[ip] = counts.get(ip, 0) + 1
        return counts[ip]

    monkeypatch.setattr(gw, "record_unknown_handler", fake_record)
    monkeypatch.setattr(gw, "mark_ip_banned", lambda session, ip: None)

    req = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "Task.submit",
        "params": {"pool": "p", "payload": {"action": "bogus"}, "taskId": None},
    }

    from fastapi.testclient import TestClient

    client = TestClient(gw.app)
    resp = client.post("/rpc", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert data["error"]["code"] == -32601
    assert counts
