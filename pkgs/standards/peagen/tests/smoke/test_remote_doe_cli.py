import os
import subprocess
from pathlib import Path

import httpx
import pytest

WORKER_LIST = "Worker.list"

pytestmark = pytest.mark.smoke

GATEWAY = os.environ.get("PEAGEN_TEST_GATEWAY", "http://localhost:8000/rpc")
REPO = "testproject"


def _gateway_available(url: str) -> bool:
    """Return ``True`` if the gateway RPC endpoint accepts POST requests."""
    envelope = {"jsonrpc": "2.0", "method": WORKER_LIST, "params": {}, "id": 0}
    try:
        response = httpx.post(url, json=envelope, timeout=5)
    except Exception:
        return False
    return response.status_code == 200


@pytest.mark.i9n
def test_remote_doe_gen(tmp_path: Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    base = Path(__file__).resolve().parents[2] / "tests" / "examples" / "locking_demo"
    spec = base / "doe_spec.yaml"
    template = base / "template_project.yaml"
    output = tmp_path / "payloads.yaml"

    result = subprocess.run(
        [
            "peagen",
            "remote",
            "--gateway-url",
            GATEWAY,
            "doe",
            "gen",
            str(spec),
            str(template),
            "--output",
            str(output),
            "--repo",
            REPO,
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )

    assert "Submitted task" in result.stdout


@pytest.mark.i9n
def test_remote_doe_process(tmp_path: Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    base = Path(__file__).resolve().parents[2] / "tests" / "examples" / "locking_demo"
    spec = base / "doe_spec.yaml"
    template = base / "template_project.yaml"
    output = tmp_path / "payloads.yaml"

    result = subprocess.run(
        [
            "peagen",
            "remote",
            "--gateway-url",
            GATEWAY,
            "doe",
            "process",
            str(spec),
            str(template),
            "--output",
            str(output),
            "--repo",
            REPO,
            "--watch",
            "--interval",
            "2",
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=180,
    )

    assert "Submitted task" in result.stdout
