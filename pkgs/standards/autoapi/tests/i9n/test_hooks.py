import pytest
from autoapi.v2 import Phase


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hooks_modify_request_and_response(api_client):
    client, api, _ = await api_client

    @api.hook(Phase.PRE_TX_BEGIN, method="Items.create")
    async def upcase(ctx):
        ctx["env"].params["name"] = ctx["env"].params["name"].upper()

    @api.hook(Phase.POST_RESPONSE, method="Items.create")
    async def enrich(ctx):
        ctx["response"].result["hooked"] = True

    t = await client.post("/tenants", json={"name": "tenant"})
    tid = t.json()["id"]
    res = await client.post(
        "/rpc",
        json={"method": "Items.create", "params": {"tenant_id": tid, "name": "foo"}},
    )
    data = res.json()["result"]
    assert data["name"] == "FOO"
    assert data["hooked"] is True
