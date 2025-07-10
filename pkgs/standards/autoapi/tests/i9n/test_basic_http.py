import pytest


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_basic_endpoints(api_client):
    client, _, _ = api_client

    resp = await client.get("/openapi.json")
    assert resp.status_code == 200

    health = await client.get("/healthz")
    assert health.status_code == 200
    assert health.json().get("ok") is True

    methodz = await client.get("/methodz")
    assert methodz.status_code == 200
    assert methodz.json()

    rpc_resp = await client.post("/rpc", json={"method": "noop", "params": {}, "id": 1})
    assert rpc_resp.status_code == 200
