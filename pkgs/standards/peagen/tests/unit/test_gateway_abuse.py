import pytest

from peagen.plugins.queues.in_memory_queue import InMemoryQueue


@pytest.mark.unit
@pytest.mark.asyncio
async def test_prevalidate_rejects_and_bans(monkeypatch):
    q = InMemoryQueue()

    class DummyBackend:
        async def store(self, task_run):
            pass

    counts = {}
    banned = {}

    async def fake_record(session, ip):
        counts[ip] = counts.get(ip, 0) + 1
        return counts[ip]

    async def fake_mark(session, ip):
        banned[ip] = True

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
    monkeypatch.setattr(gw, "record_unknown_handler", fake_record)
    monkeypatch.setattr(gw, "mark_ip_banned", fake_mark)

    # first nine invalid calls -> not banned
    payload = {"id": "1"}  # missing method
    for _ in range(9):
        resp = await gw._prevalidate(payload, "1.1.1.1")
        assert resp["error"]["code"] == -32601
    assert "1.1.1.1" not in banned

    # tenth call triggers ban
    resp = await gw._prevalidate(payload, "1.1.1.1")
    assert resp["error"]["code"] == -32601
    assert banned.get("1.1.1.1") is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_prevalidate_unknown_method(monkeypatch):
    q = InMemoryQueue()

    class DummyBackend:
        async def store(self, task_run):
            pass

    async def fake_record(session, ip):
        return 1

    async def fake_mark(session, ip):
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
    monkeypatch.setattr(gw, "record_unknown_handler", fake_record)
    monkeypatch.setattr(gw, "mark_ip_banned", fake_mark)

    payload = {"id": "1", "method": "Foo.Bar"}
    resp = await gw._prevalidate(payload, "2.2.2.2")
    assert resp["error"]["code"] == -32601
