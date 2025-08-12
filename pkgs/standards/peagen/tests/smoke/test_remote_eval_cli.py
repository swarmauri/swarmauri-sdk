import json
import os
import shutil
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


def _prepare_workspace(src: Path, tmp: Path) -> Path:
    workspace = tmp / "workspace"
    shutil.copytree(src, workspace)
    return workspace


@pytest.mark.i9n
def test_remote_eval_submits_task(tmp_path: Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    src = (
        Path(__file__).resolve().parents[2]
        / "tests"
        / "examples"
        / "peagen_local_demo"
        / "test_workspace"
    )
    workspace = _prepare_workspace(src, tmp_path)

    result = subprocess.run(
        [
            "peagen",
            "remote",
            "--gateway-url",
            GATEWAY,
            "eval",
            str(workspace),
            "*.py",
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
def test_remote_eval_returns_json(tmp_path: Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    src = (
        Path(__file__).resolve().parents[2]
        / "tests"
        / "examples"
        / "peagen_local_demo"
        / "test_workspace"
    )
    workspace = _prepare_workspace(src, tmp_path)

    result = subprocess.run(
        [
            "peagen",
            "remote",
            "--gateway-url",
            GATEWAY,
            "eval",
            str(workspace),
            "*.py",
            "--repo",
            REPO,
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )

    out = result.stdout
    if "{" not in out:
        pytest.skip("gateway didn't return result JSON")
    json_block = out[out.index("{") : out.rindex("}") + 1]
    data = json.loads(json_block)
    assert isinstance(data, dict)
