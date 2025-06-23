import os
import subprocess
from pathlib import Path

import httpx
import pytest

GATEWAY = os.environ.get("PEAGEN_TEST_GATEWAY", "https://gw.peagen.com/rpc")


def _gateway_available(url: str) -> bool:
    """Return ``True`` if the gateway RPC endpoint accepts POST requests."""
    envelope = {"jsonrpc": "2.0", "method": "Worker.list", "params": {}, "id": 0}
    try:
        response = httpx.post(url, json=envelope, timeout=5)
    except Exception:
        return False
    return response.status_code < 500


@pytest.mark.i9n
def test_remote_fetch_repo(tmp_path: Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    repo = "https://github.com/swarmauri/swarmauri-sdk.git"
    result = subprocess.run(
        [
            "peagen",
            "remote",
            "--gateway-url",
            GATEWAY,
            "fetch",
            "--repo",
            repo,
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )

    assert result.returncode != 0
    assert "Remote error" in result.stderr


@pytest.mark.i9n
def test_remote_fetch_uri(tmp_path: Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    uri = "git+https://github.com/swarmauri/swarmauri-sdk.git@HEAD"
    result = subprocess.run(
        [
            "peagen",
            "remote",
            "--gateway-url",
            GATEWAY,
            "fetch",
            uri,
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )

    assert result.returncode != 0
    assert "Remote error" in result.stderr
