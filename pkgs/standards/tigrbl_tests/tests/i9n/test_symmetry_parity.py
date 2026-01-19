import pytest

CRUD_MAP = {
    "create": ("post", "/tenant/{tenant_id}/item"),
    "list": ("get", "/tenant/{tenant_id}/item"),
    "clear": ("delete", "/tenant/{tenant_id}/item"),
    "read": ("get", "/tenant/{tenant_id}/item/{item_id}"),
    "update": ("patch", "/tenant/{tenant_id}/item/{item_id}"),
    "delete": ("delete", "/tenant/{tenant_id}/item/{item_id}"),
}


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_route_and_method_symmetry(api_client):
    client, api, _ = api_client
    api.attach_diagnostics(prefix="", app=client._transport.app)
    spec = (await client.get("/openapi.json")).json()
    paths = spec["paths"]
    methods = await client.get("/methodz")
    method_list = {m["method"] for m in methods.json()["methods"]}

    for verb, (http_verb, path) in CRUD_MAP.items():
        assert path in paths
        assert http_verb in paths[path]
        assert f"Item.{verb}" in method_list
