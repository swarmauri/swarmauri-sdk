import json
import os
import subprocess

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
def test_login_and_fetch_keys(tmp_path):
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    subprocess.run(
        ["peagen", "login", "--gateway-url", GATEWAY],
        check=True,
        timeout=60,
    )

    result = subprocess.run(
        ["peagen", "keys", "fetch-server", "--gateway-url", GATEWAY],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    data = json.loads(result.stdout)
    assert isinstance(data, dict)


@pytest.mark.i9n
def test_secret_roundtrip(tmp_path):
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    subprocess.run(
        [
            "peagen",
            "remote",
            "--gateway-url",
            GATEWAY,
            "secrets",
            "add",
            "smoke-secret",
            "value",
        ],
        check=True,
        timeout=60,
    )

    subprocess.run(
        [
            "peagen",
            "remote",
            "--gateway-url",
            GATEWAY,
            "secrets",
            "remove",
            "smoke-secret",
        ],
        check=True,
        timeout=60,
    )
