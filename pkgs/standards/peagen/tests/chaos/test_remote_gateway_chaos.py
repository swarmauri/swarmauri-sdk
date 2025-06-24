import asyncio
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


@pytest.mark.chaos
def test_remote_gateway_invalid_method() -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    envelope = {"jsonrpc": "2.0", "method": "Nope.nothing", "params": {}, "id": 1}
    response = httpx.post(GATEWAY, json=envelope, timeout=5)
    assert response.status_code == 200
    data = response.json()
    assert "error" in data


async def _worker_list(client: httpx.AsyncClient) -> bool:
    envelope = {"jsonrpc": "2.0", "method": "Worker.list", "params": {}, "id": 0}
    resp = await client.post(GATEWAY, json=envelope, timeout=5)
    return resp.status_code == 200


@pytest.mark.chaos
@pytest.mark.asyncio
async def test_remote_gateway_worker_list_heavy_load() -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*[_worker_list(client) for _ in range(10)])
    assert all(results)


@pytest.mark.chaos
def test_remote_gateway_large_payload() -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    large = "x" * 10000
    envelope = {
        "jsonrpc": "2.0",
        "method": "Task.submit",
        "params": {"pool": "default", "payload": {"data": large}},
        "id": 2,
    }
    response = httpx.post(GATEWAY, json=envelope, timeout=5)
    assert response.status_code == 200
    data = response.json()
    assert "result" in data or "error" in data
