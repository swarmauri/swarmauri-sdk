import multiprocessing as mp
import queue
import time

import pytest
from typer.testing import CliRunner

from peagen.commands.process import process_app


# Helper worker for simulation

def _worker(task_q, result_q, ack_dict):
    try:
        task = task_q.get(timeout=0.1)
    except queue.Empty:
        return
    # Simulate long-running task
    time.sleep(1)
    result_q.put(task)
    ack_dict[task] = True


@pytest.mark.chaos
def test_worker_reclaim_after_kill(monkeypatch):
    task_q = mp.Queue()
    result_q = mp.Queue()
    manager = mp.Manager()
    ack = manager.dict()

    task_q.put("task1")
    p = mp.Process(target=_worker, args=(task_q, result_q, ack))
    p.start()
    time.sleep(0.2)
    p.kill()
    p.join()

    assert not ack.get("task1")
    task_q.put("task1")  # spawner requeues

    p2 = mp.Process(target=_worker, args=(task_q, result_q, ack))
    p2.start()
    p2.join()

    assert result_q.get(timeout=2) == "task1"
    assert ack["task1"] is True


@pytest.mark.chaos
def test_cli_exits_when_redis_unavailable(monkeypatch, tmp_path):
    payload = tmp_path / "proj.yaml"
    payload.write_text("schemaVersion: '1.0'\nPROJECTS: []", encoding="utf-8")

    def fail_from_url(*args, **kwargs):
        raise ConnectionError("cannot connect")

    monkeypatch.setattr(
        "peagen.publishers.redis_publisher.redis.from_url", fail_from_url
    )

    runner = CliRunner()
    result = runner.invoke(
        process_app, [str(payload), "--notify", "redis://localhost"]
    )
    assert result.exit_code != 0


class _DummyAgent:
    def __init__(self):
        self.calls = 0

    def exec(self, *a, **k):
        self.calls += 1
        if self.calls <= 5:
            from httpx import HTTPStatusError, Response, Request

            raise HTTPStatusError(
                "503", request=Request("POST", "http://x"), response=Response(503)
            )
        return "ok"

    conversation = None


@pytest.mark.chaos
def test_llm_503_retries(monkeypatch):
    monkeypatch.setattr("peagen._external.QAAgent", lambda llm: _DummyAgent())
    monkeypatch.setattr(
        "peagen._external.SystemMessage", lambda content: None
    )
    monkeypatch.setattr(
        "peagen._external.GenericLLM",
        lambda: type("LLM", (), {"get_llm": lambda *a, **k: None})(),
    )

    from peagen._external import call_external_agent

    result = call_external_agent(
        "prompt", {"provider": "x", "api_key": "k", "model_name": "m"}
    )
    assert result == "ok"

