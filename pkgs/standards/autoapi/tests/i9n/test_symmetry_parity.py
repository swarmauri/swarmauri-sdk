import pytest

CRUD_MAP = {
    "create": ("post", "/items"),
    "list": ("get", "/items"),
    "clear": ("delete", "/items"),
    "read": ("get", "/items/{item_id}"),
    "update": ("patch", "/items/{item_id}"),
    "delete": ("delete", "/items/{item_id}"),
}


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_route_and_method_symmetry(api_client):
    client, _, _ = api_client
    spec = (await client.get("/openapi.json")).json()
    paths = spec["paths"]
    methods = await client.get("/methodz")
    method_list = methods.json()

    for verb, (http_verb, path) in CRUD_MAP.items():
        assert path in paths
        assert http_verb in paths[path]
        assert f"Items.{verb}" in method_list

    nested_base = "/tenants/{tenant_id}"
    assert nested_base in paths
    for verb in ("create", "list", "clear"):
        assert CRUD_MAP[verb][0] in paths[nested_base]
    nested_item = "/tenants/{tenant_id}/{item_id}"
    assert nested_item in paths
    for verb in ("read", "update", "delete"):
        assert CRUD_MAP[verb][0] in paths[nested_item]
