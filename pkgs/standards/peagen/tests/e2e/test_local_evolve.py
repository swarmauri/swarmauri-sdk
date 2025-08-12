import json
import os
import shutil
import subprocess
from pathlib import Path

import httpx
import pytest

WORKER_LIST = "Worker.list"

pytestmark = pytest.mark.e2e

EXAMPLES = Path(__file__).resolve().parents[1] / "examples" / "peagen_local_demo"
GATEWAY = os.environ.get("PEAGEN_TEST_GATEWAY", "http://localhost:8000/rpc")


def _gateway_available(url: str) -> bool:
    envelope = {"jsonrpc": "2.0", "method": WORKER_LIST, "params": {}, "id": 0}
    try:
        response = httpx.post(url, json=envelope, timeout=5)
    except Exception:
        return False
    return response.status_code == 200


def test_local_evolve(tmp_path: Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")
    demo = tmp_path / "demo"
    shutil.copytree(EXAMPLES, demo)
    env = os.environ.copy()
    env.setdefault("GROQ_API_KEY", "dummy")
    env.setdefault("PEAGEN_GATEWAY", GATEWAY)
    spec = demo / "test_evolve_spec.yaml"
    result = subprocess.run(
        ["peagen", "local", "-q", "evolve", str(spec)],
        cwd=demo,
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
        env=env,
    )
    last_line = result.stdout.strip().splitlines()[-1]
    data = json.loads(last_line)
    assert data.get("status") == "success"
