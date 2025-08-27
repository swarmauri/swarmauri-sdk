import pytest


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_list_filters_optional(api_client):
    client, _, _ = api_client

    spec = (await client.get("/openapi.json")).json()
    params = spec["paths"]["/tenant"]["get"].get("parameters", [])

    # If a specific filter parameter like "name" is present, ensure it's optional.
    name_param = next((p for p in params if p.get("name") == "name"), None)
    if name_param is not None:
        assert name_param.get("required") is False
    else:
        # Otherwise verify that no query parameters are marked as required.
        assert all(p.get("required") is False for p in params)

    r = await client.get("/tenant")
    assert r.status_code == 200
    assert r.json() == []

    r2 = await client.get("/tenant", params={"name": "foo"})
    assert r2.status_code == 200
    assert r2.json() == []
