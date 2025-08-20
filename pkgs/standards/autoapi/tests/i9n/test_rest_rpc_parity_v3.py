import pytest


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_create_parity(api_client_v3):
    client, _, _, _ = api_client_v3
    payload = {"name": "gadget", "secret": "sec"}

    rest_resp = await client.post("/widget", json=payload)
    rpc_resp = await client.post(
        "/rpc/",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "Widget.create",
            "params": payload,
        },
    )

    rest_data = rest_resp.json()
    rpc_data = rpc_resp.json()["result"]

    rest_filtered = {k: v for k, v in rest_data.items() if k != "id"}
    rpc_filtered = {k: v for k, v in rpc_data.items() if k != "id"}
    assert rest_filtered == rpc_filtered


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_read_parity(api_client_v3):
    client, _, _, _ = api_client_v3
    create_payload = {"name": "reader", "secret": "s1"}
    created = await client.post("/widget", json=create_payload)
    wid = created.json()["id"]

    rest_resp = await client.get(f"/widget/{wid}")
    rpc_resp = await client.post(
        "/rpc/",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "Widget.read",
            "params": {"id": wid},
        },
    )

    assert rest_resp.json() == rpc_resp.json()["result"]


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_delete_parity(api_client_v3):
    client, _, _, _ = api_client_v3
    w1 = (await client.post("/widget", json={"name": "a", "secret": "s"})).json()
    w2 = (await client.post("/widget", json={"name": "b", "secret": "s"})).json()

    rest_del = await client.delete(f"/widget/{w1['id']}")
    assert rest_del.status_code == 204
    rpc_read = await client.post(
        "/rpc/",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "Widget.read",
            "params": {"id": w1["id"]},
        },
    )
    err = rpc_read.json()["error"]
    assert err["code"] == -32003

    rpc_del = await client.post(
        "/rpc/",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "Widget.delete",
            "params": {"id": w2["id"]},
        },
    )
    assert rpc_del.json()["result"]["deleted"] == 1
    rest_read = await client.get(f"/widget/{w2['id']}")
    assert rest_read.status_code == 404


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_list_parity(api_client_v3):
    client, _, _, _ = api_client_v3
    await client.post("/widget", json={"name": "a", "secret": "s"})
    await client.post("/widget", json={"name": "b", "secret": "s"})

    rest_resp = await client.get("/widget")
    rpc_resp = await client.post(
        "/rpc/",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "Widget.list",
            "params": {"filters": {}},
        },
    )

    rest_names = sorted([w["name"] for w in rest_resp.json()])
    rpc_names = sorted([w["name"] for w in rpc_resp.json()["result"]])
    assert rest_names == rpc_names == ["a", "b"]


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_clear_parity(api_client_v3):
    client, _, _, _ = api_client_v3
    await client.post("/widget", json={"name": "a", "secret": "s"})
    await client.post("/widget", json={"name": "b", "secret": "s"})

    rest_clear = await client.delete("/widget")
    assert rest_clear.status_code == 204
    rpc_list = await client.post(
        "/rpc/",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "Widget.list",
            "params": {"filters": {}},
        },
    )
    assert rpc_list.json()["result"] == []

    await client.post("/widget", json={"name": "c", "secret": "s"})
    await client.post("/widget", json={"name": "d", "secret": "s"})

    rpc_clear = await client.post(
        "/rpc/",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "Widget.clear",
            "params": {"filters": {}},
        },
    )
    assert rpc_clear.json()["result"]["deleted"] == 2
    rest_list = await client.get("/widget")
    assert rest_list.json() == []
