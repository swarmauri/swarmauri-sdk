import os
import subprocess

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
    return response.status_code == 200


@pytest.mark.i9n
def test_unknown_rpc_method() -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")
    envelope = {"jsonrpc": "2.0", "method": "Foo.Bar", "params": {}, "id": 1}
    resp = httpx.post(GATEWAY, json=envelope, timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert data["error"]["code"] == -32601
    assert data["error"]["data"]["method"] == "Foo.Bar"


@pytest.mark.i9n
def test_unknown_cli_subcommand() -> None:
    result = subprocess.run(
        ["peagen", "remote", "foo", "--gateway-url", GATEWAY],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "No such command" in result.stderr
