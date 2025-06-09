import time
import pytest

from peagen.worker.base import WorkerBase


@pytest.mark.unit
@pytest.mark.asyncio
async def test_worker_circuit_breaker(monkeypatch):
    worker = WorkerBase(
        gateway="http://example.com",
        host="127.0.0.1",
        port=8001,
        fail_max=1,
        reset_timeout=10,
    )

    async def failing(task):
        raise RuntimeError("boom")

    async def success(task):
        return {"ok": True}

    worker.register_handler("fail", failing)
    worker.register_handler("ok", success)

    sent = []

    async def fake_notify(state, task_id, result=None):
        sent.append((state, result))

    worker._notify = fake_notify

    await worker._run_task({"id": "t1", "payload": {"action": "fail"}})
    assert sent[-1][0] == "failed"
    assert worker._failure_count == 1
    assert worker._circuit_open_until > time.time()

    await worker._run_task({"id": "t2", "payload": {"action": "fail"}})
    assert sent[-1][1]["error"] == "Circuit open"

    worker._circuit_open_until = time.time() - 1
    await worker._run_task({"id": "t3", "payload": {"action": "ok"}})
    assert sent[-1][0] == "success"
    assert worker._failure_count == 0
    assert worker._circuit_open_until == 0.0
