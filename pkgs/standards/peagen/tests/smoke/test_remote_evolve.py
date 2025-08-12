import json
import os
import subprocess
from pathlib import Path

import httpx
import pytest

WORKER_LIST = "Worker.list"

pytestmark = pytest.mark.smoke

GATEWAY = os.environ.get("PEAGEN_TEST_GATEWAY", "http://localhost:8000/rpc")
REPO = "testproject"

SPEC_PATH = (
    Path(__file__).resolve().parents[2]
    / "tests"
    / "examples"
    / "simple_evolve_demo"
    / "evolve_remote_spec.yaml"
)


def _gateway_available(url: str) -> bool:
    """Return ``True`` if the gateway RPC endpoint accepts POST requests."""
    envelope = {"jsonrpc": "2.0", "method": WORKER_LIST, "params": {}, "id": 0}
    try:
        resp = httpx.post(url, json=envelope, timeout=5)
    except Exception:
        return False
    return resp.status_code == 200


@pytest.mark.i9n
def test_remote_evolve(tmp_path: Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    cmd = [
        "peagen",
        "remote",
        "-q",
        "--gateway-url",
        GATEWAY,
        "evolve",
        str(SPEC_PATH),
        "--watch",
        "--repo",
        REPO,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)
    out = result.stdout
    lines = out.splitlines()
    for idx in range(len(lines) - 1, -1, -1):
        if lines[idx].startswith("{"):
            json_block = "\n".join(lines[idx:])
            break
    data = json.loads(json_block)
    assert data["status"] == "success"
