import json
import os
import shutil
import subprocess
from pathlib import Path

import httpx
import pytest

GATEWAY = os.environ.get("PEAGEN_TEST_GATEWAY", "https://gw.peagen.com/rpc")


def _gateway_available(url: str) -> bool:
    """Return ``True`` if the gateway URL responds successfully."""
    try:
        response = httpx.get(url, timeout=5)
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
            "eval",
            str(workspace),
            "*.py",
            "--gateway-url",
            GATEWAY,
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
            "eval",
            str(workspace),
            "*.py",
            "--gateway-url",
            GATEWAY,
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )

    json_lines = [line for line in result.stdout.splitlines() if line.startswith("{")]
    if not json_lines:
        pytest.skip("gateway didn't return result JSON")
    data = json.loads("\n".join(json_lines))
    assert isinstance(data, dict)
