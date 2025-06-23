import os
import subprocess

import httpx
import pytest

GATEWAY = os.environ.get("PEAGEN_TEST_GATEWAY", "https://gw.peagen.com/rpc")


def _gateway_available(url: str) -> bool:
    """Return ``True`` if the gateway URL responds successfully."""
    try:
        response = httpx.get(url, timeout=5)
    except Exception:
        return False
    return response.status_code < 500


@pytest.mark.i9n
def test_remote_mutate_submit(tmp_path: str) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    repo = "https://github.com/swarmauri/swarmauri-sdk.git"
    workspace = "pkgs/standards/peagen/tests/examples/peagen_local_demo/test_workspace"

    result = subprocess.run(
        [
            "peagen",
            "remote",
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
            "--gateway-url",
            GATEWAY,
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )

    assert "Submitted task" in result.stdout
