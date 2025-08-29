import inspect
import pytest
from autoapi.v3.compat.transactional import transactional
from autoapi.v3.types import UUID


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_transaction_decorator(api_client):
    client, api, Item = api_client

    async def fail(payload, db):
        obj = Item(tenant_id=UUID(payload["tenant_id"]), name=payload["name"])
        db.add(obj)
        rv = db.flush()
        if inspect.isawaitable(rv):
            await rv
        if payload.get("fail"):
            raise ValueError("boom")
        return {"id": obj.id}

    fail = transactional(api, fail)

    t = await client.post("/tenant", json={"name": "tx"})
    tid = t.json()["id"]

    bad = await client.post(
        "/rpc",
        json={
            "method": "Txn.fail",
            "params": {"tenant_id": tid, "name": "a", "fail": True},
        },
    )
    assert bad.json()["error"] is not None

    lst = await client.post("/rpc", json={"method": "Item.list", "params": {}})
    assert lst.json()["result"] == []

    ok = await client.post(
        "/rpc",
        json={"method": "Txn.fail", "params": {"tenant_id": tid, "name": "b"}},
    )
    assert ok.json()["result"]["id"]
    lst2 = await client.post("/rpc", json={"method": "Item.list", "params": {}})
    assert len(lst2.json()["result"]) == 1
