import pytest


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rest_rpc_parity(api_client):
    client, _, Item = await api_client
    t = await client.post("/tenants", json={"name": "acme"})
    tenant_id = t.json()["id"]

    rest = await client.post("/items", json={"tenant_id": tenant_id, "name": "foo"})
    item = rest.json()

    rpc = await client.post(
        "/rpc",
        json={
            "method": "Items.create",
            "params": {"tenant_id": tenant_id, "name": "foo"},
        },
    )
    rpc_item = rpc.json()["result"]
    assert item["name"] == rpc_item["name"]
    assert item["tenant_id"] == rpc_item["tenant_id"]

    rid = item["id"]
    rest_read = await client.get(f"/items/{rid}")
    rpc_read = await client.post(
        "/rpc", json={"method": "Items.read", "params": {"id": rid}}
    )
    assert rest_read.json() == rpc_read.json()["result"]

    rest_list = await client.get("/items")
    rpc_list = await client.post("/rpc", json={"method": "Items.list"})
    assert len(rest_list.json()) == len(rpc_list.json()["result"])
