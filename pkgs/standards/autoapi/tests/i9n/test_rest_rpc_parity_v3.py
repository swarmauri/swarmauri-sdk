import pytest


async def _rpc(client, method, params):
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    return await client.post("/rpc/", json=payload)


@pytest.mark.i9n
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "verb",
    ["create", "read", "update", "replace", "delete", "list", "clear"],
)
async def test_rest_rpc_parity_default_ops(api_client_v3, verb):
    client, _, _, _ = api_client_v3
    base_payload = {"name": "gadget", "secret": "sec"}

    if verb == "create":
        rest_resp = await client.post("/Widget", json=base_payload)
        rpc_resp = await _rpc(client, "Widget.create", base_payload)
        rest_filtered = {k: v for k, v in rest_resp.json().items() if k != "id"}
        rpc_filtered = {k: v for k, v in rpc_resp.json()["result"].items() if k != "id"}
        assert rest_filtered == rpc_filtered

    elif verb == "read":
        w1 = (await client.post("/Widget", json=base_payload)).json()
        w2 = (await client.post("/Widget", json=base_payload)).json()
        rest_resp = await client.get(f"/Widget/{w1['id']}")
        rpc_resp = await _rpc(client, "Widget.read", {"id": w2["id"]})
        assert rest_resp.json() == rpc_resp.json()["result"]

    elif verb == "update":
        w1 = (await client.post("/Widget", json=base_payload)).json()
        w2 = (await client.post("/Widget", json=base_payload)).json()
        patch = {"name": "updated"}
        rest_resp = await client.patch(f"/Widget/{w1['id']}", json=patch)
        rpc_resp = await _rpc(client, "Widget.update", {"id": w2["id"], **patch})
        rest_filtered = {k: v for k, v in rest_resp.json().items() if k != "id"}
        rpc_filtered = {k: v for k, v in rpc_resp.json()["result"].items() if k != "id"}
        assert rest_filtered == rpc_filtered

    elif verb == "replace":
        w1 = (await client.post("/Widget", json=base_payload)).json()
        w2 = (await client.post("/Widget", json=base_payload)).json()
        repl = {"name": "replacement", "secret": "zzz"}
        rest_resp = await client.put(f"/Widget/{w1['id']}", json=repl)
        rpc_resp = await _rpc(client, "Widget.replace", {"id": w2["id"], **repl})
        rest_filtered = {k: v for k, v in rest_resp.json().items() if k != "id"}
        rpc_filtered = {k: v for k, v in rpc_resp.json()["result"].items() if k != "id"}
        assert rest_filtered == rpc_filtered

    elif verb == "delete":
        w1 = (await client.post("/Widget", json=base_payload)).json()
        w2 = (await client.post("/Widget", json=base_payload)).json()
        rest_del = await client.delete(f"/Widget/{w1['id']}")
        assert rest_del.status_code == 204
        rpc_read = await _rpc(client, "Widget.read", {"id": w1["id"]})
        assert rpc_read.json()["error"]["code"] == -32003
        rpc_del = await _rpc(client, "Widget.delete", {"id": w2["id"]})
        assert rpc_del.json()["result"]["deleted"] == 1
        rest_read = await client.get(f"/Widget/{w2['id']}")
        assert rest_read.status_code == 404

    elif verb == "list":
        await client.post("/Widget", json={"name": "a", "secret": "s"})
        await client.post("/Widget", json={"name": "b", "secret": "s"})
        rest_resp = await client.get("/Widget")
        rpc_resp = await _rpc(client, "Widget.list", {"filters": {}})
        rest_names = sorted([w["name"] for w in rest_resp.json()])
        rpc_names = sorted([w["name"] for w in rpc_resp.json()["result"]])
        assert rest_names == rpc_names == ["a", "b"]

    elif verb == "clear":
        await client.post("/Widget", json={"name": "a", "secret": "s"})
        await client.post("/Widget", json={"name": "b", "secret": "s"})
        rest_clear = await client.delete("/Widget")
        assert rest_clear.status_code == 204
        rpc_list = await _rpc(client, "Widget.list", {"filters": {}})
        assert rpc_list.json()["result"] == []
        await client.post("/Widget", json={"name": "c", "secret": "s"})
        await client.post("/Widget", json={"name": "d", "secret": "s"})
        rpc_clear = await _rpc(client, "Widget.clear", {"filters": {}})
        assert rpc_clear.json()["result"]["deleted"] == 2
        rest_list = await client.get("/Widget")
        assert rest_list.json() == []


@pytest.mark.i9n
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "verb",
    ["bulk_create", "bulk_update", "bulk_replace", "bulk_delete"],
)
async def test_rest_rpc_parity_bulk_ops(api_client_v3, verb):
    client, _, _, _ = api_client_v3

    if verb == "bulk_create":
        rows = [{"name": "a", "secret": "s"}, {"name": "b", "secret": "s"}]
        rest_resp = await client.post("/Widget/bulk", json={"rows": rows})
        rpc_resp = await _rpc(client, "Widget.bulk_create", {"rows": rows})
        rest_names = sorted(r["name"] for r in rest_resp.json())
        rpc_names = sorted(r["name"] for r in rpc_resp.json()["result"])
        assert rest_names == rpc_names == ["a", "b"]

    elif verb == "bulk_update":
        r1 = (await client.post("/Widget", json={"name": "a", "secret": "s"})).json()
        r2 = (await client.post("/Widget", json={"name": "b", "secret": "s"})).json()
        r3 = (await client.post("/Widget", json={"name": "a", "secret": "s"})).json()
        r4 = (await client.post("/Widget", json={"name": "b", "secret": "s"})).json()
        rest_rows = [{"id": r1["id"], "name": "x"}, {"id": r2["id"], "name": "y"}]
        rpc_rows = [{"id": r3["id"], "name": "x"}, {"id": r4["id"], "name": "y"}]
        rest_resp = await client.patch("/Widget/bulk", json={"rows": rest_rows})
        rpc_resp = await _rpc(client, "Widget.bulk_update", {"rows": rpc_rows})
        rest_filtered = sorted(
            {k: v for k, v in row.items() if k != "id"} for row in rest_resp.json()
        )
        rpc_filtered = sorted(
            {k: v for k, v in row.items() if k != "id"}
            for row in rpc_resp.json()["result"]
        )
        assert rest_filtered == rpc_filtered

    elif verb == "bulk_replace":
        r1 = (await client.post("/Widget", json={"name": "a", "secret": "s"})).json()
        r2 = (await client.post("/Widget", json={"name": "b", "secret": "s"})).json()
        r3 = (await client.post("/Widget", json={"name": "a", "secret": "s"})).json()
        r4 = (await client.post("/Widget", json={"name": "b", "secret": "s"})).json()
        rest_rows = [
            {"id": r1["id"], "name": "m", "secret": "s1"},
            {"id": r2["id"], "name": "n", "secret": "s2"},
        ]
        rpc_rows = [
            {"id": r3["id"], "name": "m", "secret": "s1"},
            {"id": r4["id"], "name": "n", "secret": "s2"},
        ]
        rest_resp = await client.put("/Widget/bulk", json={"rows": rest_rows})
        rpc_resp = await _rpc(client, "Widget.bulk_replace", {"rows": rpc_rows})
        rest_filtered = sorted(
            {k: v for k, v in row.items() if k != "id"} for row in rest_resp.json()
        )
        rpc_filtered = sorted(
            {k: v for k, v in row.items() if k != "id"}
            for row in rpc_resp.json()["result"]
        )
        assert rest_filtered == rpc_filtered

    elif verb == "bulk_delete":
        r1 = (await client.post("/Widget", json={"name": "a", "secret": "s"})).json()
        r2 = (await client.post("/Widget", json={"name": "b", "secret": "s"})).json()
        r3 = (await client.post("/Widget", json={"name": "c", "secret": "s"})).json()
        r4 = (await client.post("/Widget", json={"name": "d", "secret": "s"})).json()
        rest_del = await client.delete(
            "/Widget/bulk", json={"ids": [r1["id"], r2["id"]]}
        )
        assert rest_del.status_code == 200
        rpc_list = await _rpc(client, "Widget.list", {"filters": {}})
        remaining = {row["id"] for row in rpc_list.json()["result"]}
        assert remaining == {r3["id"], r4["id"]}
        rpc_del = await _rpc(
            client, "Widget.bulk_delete", {"ids": [r3["id"], r4["id"]]}
        )
        assert rpc_del.json()["result"]["deleted"] == 2
        rest_list = await client.get("/Widget")
        assert rest_list.json() == []
