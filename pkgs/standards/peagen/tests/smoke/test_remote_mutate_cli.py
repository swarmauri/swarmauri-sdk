import os
import subprocess
from pathlib import Path

import httpx
import pytest

WORKER_LIST = "Worker.list"

pytestmark = pytest.mark.smoke

GATEWAY = os.environ.get("PEAGEN_TEST_GATEWAY", "http://localhost:8000/rpc")


def _gateway_available(url: str) -> bool:
    """Return ``True`` if the gateway RPC endpoint accepts POST requests."""
    envelope = {"jsonrpc": "2.0", "method": WORKER_LIST, "params": {}, "id": 0}
    try:
        response = httpx.post(url, json=envelope, timeout=5)
    except Exception:
        return False
    return response.status_code == 200


@pytest.mark.i9n
def test_remote_mutate_submit(tmp_path: str) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    repo = "testproject"
    workspace = str(
        Path(__file__).resolve().parents[2]
        / "tests"
        / "examples"
        / "peagen_local_demo"
        / "test_workspace"
    )

    result = subprocess.run(
        [
            "peagen",
            "remote",
            "--gateway-url",
            GATEWAY,
            "mutate",
            workspace,
            "--target-file",
            "main.py",
            "--import-path",
            "main",
            "--entry-fn",
            "main",
            "--repo",
            repo,
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )

    assert "Submitted task" in result.stdout
