import pytest

CRUD_MAP = {
    "create": ("post", "/item"),
    "list": ("get", "/item"),
    "clear": ("delete", "/item"),
    "read": ("get", "/item/{item_id}"),
    "update": ("patch", "/item/{item_id}"),
    "delete": ("delete", "/item/{item_id}"),
}


@pytest.mark.r8n
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
        assert f"Item.{verb}" in method_list

    nested_base = "/tenant/{tenant_id}"
    assert nested_base in paths
    for verb in ("create", "list", "clear"):
        assert CRUD_MAP[verb][0] in paths[nested_base]
    nested_item = "/tenant/{tenant_id}/{item_id}"
    assert nested_item in paths
    for verb in ("read", "update", "delete"):
        assert CRUD_MAP[verb][0] in paths[nested_item]
