"""Integration tests for `peagen evolve step` using Redis Streams."""

from __future__ import annotations

import subprocess
import time

import pytest


@pytest.fixture(scope="module", autouse=True)
def redis_compose():
    """Start and stop the Redis docker-compose service."""
    subprocess.run(["docker-compose", "-f", "ci/docker-redis.yml", "up", "-d"], check=True)
    # give redis a moment to start
    time.sleep(2)
    yield
    subprocess.run(["docker-compose", "-f", "ci/docker-redis.yml", "down"], check=True)


@pytest.mark.integration_redis
def test_evolve_step_happy_path(tmp_path):
    """Run warm-spawner with workers then execute `peagen evolve step`."""
    spawner = subprocess.Popen([
        "peagen",
        "worker",
        "warm-spawner",
        "--cpu-workers",
        "4",
    ])
    try:
        subprocess.run(["peagen", "evolve", "step"], check=True)
    finally:
        spawner.terminate()
        spawner.wait()

    metrics = subprocess.check_output(["curl", "-s", "http://localhost:9090/metrics"]).decode()
    assert 'worker_exit_reason{reason="success"} 5' in metrics

    length = subprocess.check_output(["redis-cli", "XLEN", "peagen.tasks"]).decode().strip()
    assert length == "0"

