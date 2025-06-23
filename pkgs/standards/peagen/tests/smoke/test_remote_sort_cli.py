import os
import subprocess
from pathlib import Path

import httpx
import pytest

GATEWAY = os.environ.get("PEAGEN_TEST_GATEWAY", "https://gw.peagen.com/rpc")
EXAMPLES = Path(__file__).resolve().parents[1] / "examples" / "projects_payloads"
BASE_URL = GATEWAY.removesuffix("/rpc")


def _gateway_available(url: str) -> bool:
    """Return ``True`` if the gateway URL responds successfully."""
    try:
        resp = httpx.get(url, timeout=5)
    except Exception:
        return False
    return resp.status_code < 500


@pytest.mark.i9n
def test_remote_sort_submits_task(tmp_path: Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    payload_src = EXAMPLES / "template_two_project.yaml"
    payload = tmp_path / "payload.yaml"
    payload.write_text(payload_src.read_text())

    result = subprocess.run(
        ["peagen", "remote", "--gateway-url", BASE_URL, "sort", str(payload)],
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
        ["peagen", "remote", "--gateway-url", bad_gateway, "sort", str(payload)],
        capture_output=True,
        text=True,
        check=False,
        timeout=5,
    )
    assert result.returncode != 0
    assert "Could not reach gateway" in result.stdout
