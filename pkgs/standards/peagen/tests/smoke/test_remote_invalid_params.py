import os
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
def test_invalid_request_structure() -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")
    resp = httpx.post(GATEWAY, json={}, timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert data["error"]["code"] == -32600


@pytest.mark.i9n
def test_method_not_found() -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")
    payload = {"jsonrpc": "2.0", "method": "Nope", "params": {}, "id": "1"}
    resp = httpx.post(GATEWAY, json=payload, timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert data["error"]["code"] == -32601


@pytest.mark.i9n
def test_task_submit_unknown_action() -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")
    payload = {
        "jsonrpc": "2.0",
        "method": "Task.submit",
        "params": {"pool": "default", "payload": {"action": "bogus"}},
        "id": "1",
    }
    resp = httpx.post(GATEWAY, json=payload, timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert data["error"]["code"] == -32601
