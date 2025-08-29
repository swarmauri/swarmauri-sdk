import pytest


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_nested_rest_rpc_parity(api_client, sample_tenant_data):
    client, _, _ = api_client

    # Create tenant to scope nested paths
    res = await client.post("/tenant", json=sample_tenant_data)
    assert res.status_code == 201
    tenant_id = res.json()["id"]

    # REST create does not require tenant_id in body
    res = await client.post(f"/tenant/{tenant_id}/item", json={"name": "rest"})
    assert res.status_code == 201, res.text
    rest_item_id = res.json()["id"]

    # REST read confirms tenant_id propagated from path
    res = await client.get(f"/tenant/{tenant_id}/item/{rest_item_id}")
    assert res.status_code == 200
    assert res.json()["tenant_id"] == tenant_id

    # RPC create requires tenant_id in params
    payload = {
        "jsonrpc": "2.0",
        "method": "Item.create",
        "params": {"tenant_id": tenant_id, "name": "rpc"},
        "id": 1,
    }
    res = await client.post("/rpc", json=payload)
    assert res.status_code == 200, res.text
    rpc_item_id = res.json()["result"]["id"]

    # RPC read verifies payload handling
    payload = {
        "jsonrpc": "2.0",
        "method": "Item.read",
        "params": {"tenant_id": tenant_id, "item_id": rpc_item_id},
        "id": 2,
    }
    res = await client.post("/rpc", json=payload)
    assert res.status_code == 200, res.text
    assert res.json()["result"]["tenant_id"] == tenant_id

    # OpenAPI schema for nested REST path should omit tenant_id from body
    spec = (await client.get("/openapi.json")).json()
    body_schema = spec["paths"]["/tenant/{tenant_id}/item"]["post"]["requestBody"][
        "content"
    ]["application/json"]["schema"]
    assert "tenant_id" not in body_schema.get("properties", {})
