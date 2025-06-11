import importlib
import pytest

from peagen.models import Task
from peagen.plugins.queues.in_memory_queue import InMemoryQueue

@pytest.mark.unit
@pytest.mark.asyncio
async def test_dependency_resolution(monkeypatch):
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

    async def _noop(*args, **kwargs):
        return None

    monkeypatch.setattr(gw, "_persist", _noop)
    monkeypatch.setattr(gw, "_publish_event", _noop)

    submit = gw.task_submit
    finish = gw.work_finished
    get = gw.task_get

    res = await submit(pool="p", payload={}, taskId="A", deps=None, labels=None, edge_pred=None)
    aid = res["taskId"]
    res2 = await submit(pool="p", payload={}, taskId="B", deps=[aid], edge_pred="results['A']['v']==1", labels=None)
    bid = res2["taskId"]

    # only A should be queued initially
    queued = await q.lrange(f"{gw.READY_QUEUE}:p", 0, -1)
    assert len(queued) == 1
    assert Task.model_validate_json(queued[0]).id == aid

    await finish(taskId=aid, status="success", result={"v": 1})

    # B should now be queued
    queued = await q.lrange(f"{gw.READY_QUEUE}:p", 0, -1)
    ids = [Task.model_validate_json(x).id for x in queued]
    assert bid in ids

    btask = await get(bid)
    assert btask["in_degree"] == 0
