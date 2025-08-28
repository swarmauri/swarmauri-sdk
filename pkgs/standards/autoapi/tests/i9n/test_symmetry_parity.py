import pytest
from autoapi.v3.types import SimpleNamespace

PARITY_MAP = [
    (
        "list",
        "get",
        "/item",
        "/tenant/{tenant_id}/item",
        "Item.list",
        ("tenant_id",),
    ),
    (
        "read",
        "get",
        "/item/{item_id}",
        "/tenant/{tenant_id}/item/{item_id}",
        "Item.read",
        ("tenant_id", "item_id"),
    ),
]


@pytest.mark.i9n
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "verb,http_verb,rest_path,nested_path,rpc_method,param_keys", PARITY_MAP
)
async def test_rest_nested_rpc_parity(
    api_client, verb, http_verb, rest_path, nested_path, rpc_method, param_keys
):
    client, api, _ = api_client
    api.attach_diagnostics(prefix="")
    spec = (await client.get("/openapi.json")).json()
    paths = spec["paths"]
    methods_resp = await client.get("/methodz")
    method_list = {SimpleNamespace(**m).method for m in methods_resp.json()["methods"]}

    assert rest_path in paths
    assert http_verb in paths[rest_path]
    assert nested_path in paths
    assert http_verb in paths[nested_path]
    assert f"Item.{verb}" in method_list

    tenant = (await client.post("/tenant", json={"name": "t"})).json()
    tenant_id = tenant["id"]
    item = (await client.post(f"/tenant/{tenant_id}/item", json={"name": "i"})).json()
    item_id = item["id"]

    ids = {"tenant_id": tenant_id, "item_id": item_id}
    rest_resp = await getattr(client, http_verb)(rest_path.format(**ids))
    nested_resp = await getattr(client, http_verb)(nested_path.format(**ids))
    rpc_payload = {
        "jsonrpc": "2.0",
        "method": rpc_method,
        "params": {k: ids[k] for k in param_keys},
        "id": 1,
    }
    rpc_resp = await client.post("/rpc", json=rpc_payload)

    assert rest_resp.status_code == 200
    assert nested_resp.status_code == 200
    assert rpc_resp.status_code == 200
    assert rest_resp.json() == nested_resp.json() == rpc_resp.json()["result"]
