import pytest


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_list_filters_optional(api_client):
    client, _, _ = api_client

    spec = (await client.get("/openapi.json")).json()
    params = spec["paths"]["/tenant"]["get"].get("parameters", [])
    name_param = next(p for p in params if p["name"] == "name")
    assert name_param["required"] is False

    r = await client.get("/tenant")
    assert r.status_code == 200
    assert r.json() == []

    r2 = await client.get("/tenant", params={"name": "foo"})
    assert r2.status_code == 200
    assert r2.json() == []
