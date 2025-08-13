import os
import subprocess
from pathlib import Path

import httpx
import pytest

WORKER_LIST = "Worker.list"

pytestmark = pytest.mark.smoke

GATEWAY = os.environ.get("PEAGEN_TEST_GATEWAY", "http://localhost:8000/rpc")
EXAMPLES = Path(__file__).resolve().parents[1] / "examples" / "projects_payloads"
BASE_URL = GATEWAY.removesuffix("/rpc")
REPO = "testproject"


def _gateway_available(url: str) -> bool:
    """Return ``True`` if the gateway RPC endpoint accepts POST requests."""
    envelope = {"jsonrpc": "2.0", "method": WORKER_LIST, "params": {}, "id": 0}
    try:
        resp = httpx.post(url, json=envelope, timeout=5)
    except Exception:
        return False
    return resp.status_code == 200


@pytest.mark.i9n
def test_remote_sort_submits_task(tmp_path: Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    payload_src = EXAMPLES / "template_two_project.yaml"
    payload = tmp_path / "payload.yaml"
    payload.write_text(payload_src.read_text())

    result = subprocess.run(
        [
            "peagen",
            "remote",
            "--gateway-url",
            BASE_URL,
            "sort",
            str(payload),
            "--repo",
            REPO,
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    assert "Submitted sort" in result.stdout


@pytest.mark.i9n
def test_remote_sort_unreachable(tmp_path: Path) -> None:
    bad_gateway = "http://127.0.0.1:9"
    payload_src = EXAMPLES / "template_two_project.yaml"
    payload = tmp_path / "payload.yaml"
    payload.write_text(payload_src.read_text())

    result = subprocess.run(
        [
            "peagen",
            "remote",
            "--gateway-url",
            bad_gateway,
            "sort",
            str(payload),
            "--repo",
            REPO,
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=5,
    )
    assert result.returncode != 0
    assert "Could not reach gateway" in result.stdout
