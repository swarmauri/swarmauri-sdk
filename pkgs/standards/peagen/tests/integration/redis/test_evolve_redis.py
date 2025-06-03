import subprocess
import time
from pathlib import Path

import pytest
import redis
import requests


@pytest.mark.integration_redis
def test_evolve_step_metrics_and_queue_empty(tmp_path):
    compose_file = Path(__file__).resolve().parents[5] / "ci" / "docker-redis.yml"

    subprocess.run(["docker-compose", "-f", str(compose_file), "up", "-d"], check=True)
    try:
        spawner = subprocess.Popen(["peagen", "warm-spawner", "--workers", "4"])
        try:
            subprocess.run(["peagen", "evolve", "step"], check=True)
        finally:
            spawner.terminate()
            spawner.wait()

        time.sleep(2)
        metrics = requests.get("http://localhost:8000/metrics").text
        assert 'worker_exit_reason{reason="success"} 5' in metrics

        client = redis.Redis(host="localhost", port=6379, decode_responses=True)
        assert client.xlen("peagen.tasks") == 0
    finally:
        subprocess.run(["docker-compose", "-f", str(compose_file), "down", "-v"], check=True)
