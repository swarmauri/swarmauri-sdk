import pytest


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_nested_path_schema_and_rpc(api_client):
    client, _, Item = api_client

    # Create a tenant
    tenant_res = await client.post("/tenant", json={"name": "Acme"})
    tenant_res.raise_for_status()
    tenant_id = tenant_res.json()["id"]

    # Schema should mark parent identifiers optional
    create_model = Item.schemas.create.in_
    fields = getattr(create_model, "model_fields", None)
    if fields is None:
        fields = getattr(create_model, "__fields__", {})
    assert "tenant_id" not in fields

    # REST call should inject path params
    rest_payload = [create_model(name="rest-item").model_dump(exclude_none=True)]
    rest_res = await client.post(f"/tenant/{tenant_id}/item", json=rest_payload)
    rest_res.raise_for_status()
    rest_item = rest_res.json()[0]
    assert rest_item["tenant_id"] == tenant_id

    # RPC call should succeed when tenant_id is provided explicitly
    rpc_payload = {
        "method": "Item.create",
        "params": {"tenant_id": tenant_id, "name": "rpc-item"},
    }
    rpc_res = await client.post("/rpc", json=rpc_payload)
    rpc_res.raise_for_status()
