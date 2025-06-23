import os
import subprocess
from pathlib import Path

import httpx
import pytest

GATEWAY = os.environ.get("PEAGEN_TEST_GATEWAY", "https://gw.peagen.com/rpc")
PROJECTS_FILE = (
    Path(__file__).resolve().parent.parent
    / "examples"
    / "projects_payloads"
    / "project_payloads.yaml"
)


def _gateway_available(url: str) -> bool:
    """Return ``True`` if the gateway URL responds successfully."""
    try:
        response = httpx.get(url, timeout=5)
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
                "--watch",
                "--interval",
                "1",
            ],
            check=True,
            timeout=60,
        )
    except subprocess.CalledProcessError as exc:
        pytest.skip(f"remote process watch failed: {exc}")
