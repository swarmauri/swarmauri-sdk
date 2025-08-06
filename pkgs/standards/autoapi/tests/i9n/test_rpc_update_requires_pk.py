import pytest


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rpc_update_requires_pk(api_client):
    """Ensure RPC update calls validate presence of primary key."""
    client, _, _ = api_client
    resp = await client.post(
        "/rpc", json={"method": "Items.update", "params": {"name": "foo"}}
    )
    data = resp.json()
    assert "error" in data
    assert data["error"]["code"] == -32602
