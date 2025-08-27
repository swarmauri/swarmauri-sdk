import pytest
import uuid
from autoapi.v3.compat.transactional import transactional


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_transaction_decorator(api_client):
    client, api, Item = api_client

    def fail(params, db):
        obj = Item(tenant_id=uuid.UUID(params["tenant_id"]), name=params["name"])
        db.add(obj)
        db.flush()
        if params.get("fail"):
            raise ValueError("boom")
        return {"id": obj.id}

    fail = transactional(api, fail)

    api.rpc["Item.fail"] = fail
    api._method_ids["Item.fail"] = None

    t = await client.post("/tenant", json={"name": "tx"})
    tid = t.json()["id"]

    bad = await client.post(
        "/rpc",
        json={
            "method": "Item.fail",
            "params": {"tenant_id": tid, "name": "a", "fail": True},
        },
    )
    assert bad.json()["error"] is not None

    lst = await client.get("/item")
    assert lst.json() == []

    ok = await client.post(
        "/rpc",
        json={"method": "Item.fail", "params": {"tenant_id": tid, "name": "b"}},
    )
    assert ok.json()["result"]["id"]
    lst2 = await client.get("/item")
    assert len(lst2.json()) == 1
