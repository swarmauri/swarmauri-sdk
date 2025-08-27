import pytest
from autoapi.v3.types import SimpleNamespace

CRUD_MAP = {
    "create": ("post", "/tenant/{tenant_id}"),
    "list": ("get", "/tenant/{tenant_id}"),
    "clear": ("delete", "/tenant/{tenant_id}"),
    "read": ("get", "/tenant/{tenant_id}/{item_id}"),
    "update": ("patch", "/tenant/{tenant_id}/{item_id}"),
    "delete": ("delete", "/tenant/{tenant_id}/{item_id}"),
}


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_route_and_method_symmetry(api_client):
    client, api, _ = api_client
    api.attach_diagnostics(prefix="")
    spec = (await client.get("/openapi.json")).json()
    paths = spec["paths"]
    methods = await client.get("/methodz")
    method_list = {SimpleNamespace(**m).method for m in methods.json()["methods"]}

    for verb, (http_verb, path) in CRUD_MAP.items():
        alt_path = (
            path.replace("{tenant_id}/", "{tenant_id}/item/", 1)
            if "{item_id}" in path
            else f"{path}/item"
        )
        actual = path if path in paths else alt_path
        assert actual in paths
        assert http_verb in paths[actual]
        assert f"Item.{verb}" in method_list
