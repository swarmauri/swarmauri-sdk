"""Chaos tests exercising Peagen's fault tolerance."""

import pytest

pytestchaos = pytest.importorskip("pytest_chaos")


@pytest.mark.chaos
def test_kill_worker_reclaimed(tmp_path):
    """Kill a worker mid-task and ensure it is reclaimed."""
    # Placeholder: spawn a worker process via pytest-chaos and kill it.
    worker = pytestchaos.spawn_worker("peagen")  # type: ignore[attr-defined]
    pytestchaos.kill(worker)
    result = pytestchaos.wait_for_reclaim(worker, timeout=30)
    assert result is True


@pytest.mark.chaos
def test_redis_primary_down(cli_runner):
    """Delete the Redis primary for 10 s and expect CLI failure."""
    with pytestchaos.redis.down(duration=10):
        ret = cli_runner.invoke("peagen", ["mutate", "--workers", "1"])
        assert ret.exit_code != 0


@pytest.mark.chaos
def test_llm_retry(monkeypatch):
    """Simulate LLM 503 responses and confirm retries succeed."""
    attempts = {
        "count": 0,
    }

    def mock_llm(*args, **kwargs):
        attempts["count"] += 1
        if attempts["count"] <= 5:
            raise pytestchaos.HTTP503Error("Service Unavailable")  # type: ignore[attr-defined]
        return "ok"

    monkeypatch.setattr("peagen.llm.call_llm", mock_llm)

    response = pytestchaos.retry_call(mock_llm, max_attempts=10)
    assert response == "ok"
    assert attempts["count"] == 6
