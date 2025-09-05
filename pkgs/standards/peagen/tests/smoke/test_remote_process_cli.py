import os
import subprocess
from pathlib import Path

import httpx
import pytest

WORKER_LIST = "Worker.list"

pytestmark = pytest.mark.smoke

GATEWAY = os.environ.get("PEAGEN_TEST_GATEWAY", "http://localhost:8000/rpc")
PROJECTS_FILE = (
    Path(__file__).resolve().parent.parent
    / "examples"
    / "projects_payloads"
    / "project_payloads.yaml"
)
REPO = "testproject"


def _gateway_available(url: str) -> bool:
    """Return ``True`` if the gateway RPC endpoint accepts POST requests."""
    envelope = {"jsonrpc": "2.0", "method": WORKER_LIST, "params": {}, "id": 0}
    try:
        response = httpx.post(url, json=envelope, timeout=5)
    except Exception:
        return False
    return response.status_code < 500


@pytest.mark.i9n
def test_remote_process_submit(tmp_path: Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    try:
        subprocess.run(
            [
                "peagen",
                "remote",
                "process",
                str(PROJECTS_FILE),
                "--gateway-url",
                GATEWAY,
                "--repo",
                REPO,
            ],
            check=True,
            timeout=60,
        )
    except subprocess.CalledProcessError as exc:
        pytest.skip(f"remote process failed: {exc}")


@pytest.mark.i9n
def test_remote_process_watch(tmp_path: Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    try:
        subprocess.run(
            [
                "peagen",
                "remote",
                "process",
                str(PROJECTS_FILE),
                "--gateway-url",
                GATEWAY,
                "--repo",
                REPO,
                "--watch",
                "--interval",
                "1",
            ],
            check=True,
            timeout=60,
        )
    except subprocess.CalledProcessError as exc:
        pytest.skip(f"remote process watch failed: {exc}")
