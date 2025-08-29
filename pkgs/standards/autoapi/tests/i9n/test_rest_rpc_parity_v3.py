import pytest


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rest_rpc_nested_parity(api_client, sample_tenant_data):
    """Ensure nested REST paths map cleanly to RPC payloads."""
    client, _, Item = api_client

    # Nested REST schema should drop parent identifiers
    assert "tenant_id" not in Item.schemas.create.in_.model_fields

    # Create tenant and item via REST (path supplies tenant_id)
    t = await client.post("/tenant", json=sample_tenant_data)
    tid = t.json()["id"]
    r_rest = await client.post(f"/tenant/{tid}/item", json={"name": "rest"})
    assert r_rest.status_code == 201

    # RPC call without tenant_id fails validation
    r_bad = await client.post(
        "/rpc", json={"method": "Item.create", "params": {"name": "oops"}}
    )
    assert r_bad.json()["error"] is not None
