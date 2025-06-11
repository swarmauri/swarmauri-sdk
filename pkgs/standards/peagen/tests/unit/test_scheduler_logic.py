import pytest
from peagen.models import Task, Status
import peagen.gateway as gw


@pytest.mark.unit
@pytest.mark.asyncio
async def test_deps_satisfied(monkeypatch):
    dep = Task(id="d1", pool="p", payload={}, status=Status.success, result={"s": 1})

    async def fake_load(tid: str):
        return dep if tid == "d1" else None

    monkeypatch.setattr(gw, "_load_task", fake_load)
    t = Task(pool="p", payload={}, deps=["d1"])
    assert await gw._deps_satisfied(t)

    t2 = Task(pool="p", payload={}, deps=["d1"], edge_pred="deps['d1']['s'] > 0")
    assert await gw._deps_satisfied(t2)

    t3 = Task(pool="p", payload={}, deps=["d1"], edge_pred="deps['d1']['s'] > 5")
    assert not await gw._deps_satisfied(t3)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_deps_satisfied_waiting(monkeypatch):
    dep = Task(id="d1", pool="p", payload={}, status=Status.running)

    async def fake_load(tid: str):
        return dep

    monkeypatch.setattr(gw, "_load_task", fake_load)
    t = Task(pool="p", payload={}, deps=["d1"])
    assert not await gw._deps_satisfied(t)


@pytest.mark.unit
def test_worker_supports_labels():
    worker = {"advertises": {"gpu": True, "cpu": True}}
    assert gw._worker_supports(worker, ["gpu"])
    assert gw._worker_supports(worker, [])
    assert not gw._worker_supports(worker, ["tpu"])

