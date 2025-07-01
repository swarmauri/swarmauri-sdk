import pytest

from peagen.plugins.queues.in_memory_queue import InMemoryQueue


@pytest.mark.unit
@pytest.mark.asyncio
async def test_task_submit_id_collision(monkeypatch):
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
    from peagen.transport.jsonrpc_schemas.task import SubmitParams
    from peagen.gateway.rpc import tasks as task_rpc

    orig_uuid = task_rpc.uuid.UUID

    def _maybe_invalid_uuid(*args, **kwargs):
        if kwargs:
            return orig_uuid(*args, **kwargs)
        raise ValueError

    # Force persistence branch to be skipped by invalidating UUID checks for
    # string inputs while preserving ``uuid.uuid4()`` behaviour.
    monkeypatch.setattr(task_rpc.uuid, "UUID", _maybe_invalid_uuid)

    r1 = await task_submit(SubmitParams(id="dup", pool="p", payload={}))
    r2 = await task_submit(SubmitParams(id="dup", pool="p", payload={}))
    assert r1.id == "dup"
    assert r2.id != "dup"
