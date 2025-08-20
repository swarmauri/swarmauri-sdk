import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy import Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Mapped

from autoapi.v3.autoapi import AutoAPI as AutoAPIv3
from autoapi.v3.specs import F, IO, S, acol
from autoapi.v3.tables import Base as Base3


@pytest_asyncio.fixture()
async def client_and_model():
    Base3.metadata.clear()

    class Gadget(Base3):
        __tablename__ = "gadgets"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True)
        )
        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(required_in=("create",)),
            io=IO(
                in_verbs=("create", "update", "replace"),
                out_verbs=("read", "list"),
            ),
        )
        age: Mapped[int] = acol(
            storage=S(type_=Integer, nullable=False, default=0),
            io=IO(
                in_verbs=("create", "update", "replace"),
                out_verbs=("read", "list"),
            ),
        )

        __autoapi_cols__ = {"id": id, "name": name, "age": age}

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base3.metadata.create_all)
    session_maker = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async def get_async_db():
        async with session_maker() as session:
            yield session

    app = FastAPI()
    api = AutoAPIv3(app=app, get_async_db=get_async_db)
    api.include_model(Gadget, prefix="")
    api.mount_jsonrpc(prefix="/rpc")
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    try:
        yield client, Gadget
    finally:
        await client.aclose()
        await engine.dispose()


@pytest.mark.i9n
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "verb",
    [
        "create",
        "read",
        "update",
        "replace",
        "delete",
        "list",
        "clear",
        "bulk_create",
        "bulk_update",
        "bulk_replace",
        "bulk_delete",
    ],
)
async def test_rpc_methods(verb, client_and_model):
    client, _ = client_and_model

    async def rpc(method, params, id_=1):
        payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": id_}
        return await client.post("/rpc", json=payload)

    if verb == "create":
        resp = await rpc("Gadget.create", {"name": "A", "age": 1})
        assert resp.status_code == 200
        data = resp.json()["result"]
        assert data["name"] == "A"
        assert data["age"] == 1

    elif verb == "read":
        created = await rpc("Gadget.create", {"name": "A", "age": 1})
        gid = created.json()["result"]["id"]
        resp = await rpc("Gadget.read", {"id": gid}, id_=2)
        assert resp.status_code == 200
        assert resp.json()["result"]["id"] == gid

    elif verb == "update":
        created = await rpc("Gadget.create", {"name": "A", "age": 1})
        gid = created.json()["result"]["id"]
        resp = await rpc("Gadget.update", {"id": gid, "name": "B", "age": 2}, id_=2)
        assert resp.status_code == 200
        data = resp.json()["result"]
        assert data["name"] == "B"
        assert data["age"] == 2

    elif verb == "replace":
        created = await rpc("Gadget.create", {"name": "A", "age": 1})
        gid = created.json()["result"]["id"]
        resp = await rpc("Gadget.replace", {"id": gid, "name": "C", "age": 5}, id_=2)
        assert resp.status_code == 200
        data = resp.json()["result"]
        assert data["name"] == "C"
        assert data["age"] == 5

    elif verb == "delete":
        created = await rpc("Gadget.create", {"name": "A", "age": 1})
        gid = created.json()["result"]["id"]
        resp = await rpc("Gadget.delete", {"id": gid}, id_=2)
        assert resp.status_code == 200
        assert resp.json()["result"]["deleted"] == 1
        follow = await rpc("Gadget.read", {"id": gid}, id_=3)
        assert "error" in follow.json()

    elif verb == "list":
        await rpc("Gadget.create", {"name": "A", "age": 1})
        await rpc("Gadget.create", {"name": "B", "age": 2})
        resp = await rpc("Gadget.list", {}, id_=3)
        assert resp.status_code == 200
        names = {item["name"] for item in resp.json()["result"]}
        assert names == {"A", "B"}

    elif verb == "clear":
        await rpc("Gadget.create", {"name": "A", "age": 1})
        await rpc("Gadget.create", {"name": "B", "age": 2})
        resp = await rpc("Gadget.clear", {}, id_=3)
        assert resp.status_code == 200
        assert resp.json()["result"]["deleted"] == 2
        remain = await rpc("Gadget.list", {}, id_=4)
        assert remain.json()["result"] == []

    elif verb == "bulk_create":
        resp = await rpc(
            "Gadget.bulk_create",
            {"rows": [{"name": "A", "age": 1}, {"name": "B", "age": 2}]},
        )
        assert resp.status_code == 200
        result = resp.json()["result"]
        assert {r["name"] for r in result} == {"A", "B"}

    elif verb == "bulk_update":
        created = await rpc(
            "Gadget.bulk_create",
            {"rows": [{"name": "A", "age": 1}, {"name": "B", "age": 2}]},
        )
        r = created.json()["result"]
        payload = {
            "rows": [
                {"id": r[0]["id"], "name": "A2", "age": 10},
                {"id": r[1]["id"], "name": "B2", "age": 20},
            ]
        }
        resp = await rpc("Gadget.bulk_update", payload, id_=2)
        assert resp.status_code == 200
        result = resp.json()["result"]
        assert {r["name"] for r in result} == {"A2", "B2"}

    elif verb == "bulk_replace":
        created = await rpc(
            "Gadget.bulk_create",
            {"rows": [{"name": "A", "age": 1}, {"name": "B", "age": 2}]},
        )
        r = created.json()["result"]
        payload = {
            "rows": [
                {"id": r[0]["id"], "name": "A3", "age": 11},
                {"id": r[1]["id"], "name": "B3", "age": 22},
            ]
        }
        resp = await rpc("Gadget.bulk_replace", payload, id_=2)
        assert resp.status_code == 200
        result = resp.json()["result"]
        assert {r["name"] for r in result} == {"A3", "B3"}

    elif verb == "bulk_delete":
        created = await rpc(
            "Gadget.bulk_create",
            {"rows": [{"name": "A", "age": 1}, {"name": "B", "age": 2}]},
        )
        r = created.json()["result"]
        ids = [r[0]["id"], r[1]["id"]]
        resp = await rpc("Gadget.bulk_delete", {"ids": ids}, id_=2)
        assert resp.status_code == 200
        assert resp.json()["result"]["deleted"] == 2
        remain = await rpc("Gadget.list", {}, id_=3)
        assert remain.json()["result"] == []
