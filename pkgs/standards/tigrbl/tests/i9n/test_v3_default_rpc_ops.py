import pytest
import pytest_asyncio
from tigrbl.orm.mixins import BulkCapable, Replaceable, Mergeable
from tigrbl.types import App, Integer, Mapped, String, uuid4
from httpx import AsyncClient, ASGITransport

from tigrbl import TigrblApp as Tigrblv3
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.tables import Base as Base3
from tigrbl.specs import F, IO, S, acol


@pytest_asyncio.fixture()
async def client_and_model():
    Base3.metadata.clear()
    Base3.registry.dispose()

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

        __tigrbl_cols__ = {"id": id, "name": name, "age": age}

    app = App()
    api = Tigrblv3(engine=mem())
    api.include_model(Gadget, prefix="")
    api.mount_jsonrpc(prefix="/rpc")
    await api.initialize()
    app.include_router(api.router)
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    try:
        yield client, Gadget
    finally:
        await client.aclose()


@pytest.mark.i9n
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "verb",
    ["create", "read", "update", "replace", "delete", "list", "clear"],
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


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_bulk_methods_absent(client_and_model):
    _, Gadget = client_and_model
    for name in (
        "bulk_create",
        "bulk_update",
        "bulk_replace",
        "bulk_merge",
        "bulk_delete",
    ):
        assert not hasattr(Gadget.rpc, name)


@pytest_asyncio.fixture()
async def bulk_client_and_model():
    Base3.metadata.clear()
    Base3.registry.dispose()

    class Gadget(Base3, BulkCapable, Replaceable, Mergeable):
        __tablename__ = "gadgets"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True)
        )
        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(required_in=("create",)),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )
        age: Mapped[int] = acol(
            storage=S(type_=Integer, nullable=False, default=0),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )

        __tigrbl_cols__ = {"id": id, "name": name, "age": age}

    app = App()
    api = Tigrblv3(engine=mem())
    api.include_model(Gadget, prefix="")
    api.mount_jsonrpc(prefix="/rpc")
    await api.initialize()
    app.include_router(api.router)
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    try:
        yield client, Gadget
    finally:
        await client.aclose()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rpc_bulk_ops(bulk_client_and_model):
    client, _ = bulk_client_and_model

    async def rpc(method, params, id_=1):
        payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": id_}
        return await client.post("/rpc", json=payload)

    resp = await rpc(
        "Gadget.bulk_create",
        [{"name": "A", "age": 1}, {"name": "B", "age": 2}],
    )
    assert resp.status_code == 200
    ids = [row["id"] for row in resp.json()["result"]]

    resp = await rpc(
        "Gadget.bulk_update",
        [{"id": ids[0], "age": 3}, {"id": ids[1], "age": 4}],
        id_=2,
    )
    assert resp.status_code == 200

    resp = await rpc(
        "Gadget.bulk_replace",
        [
            {"id": ids[0], "name": "C", "age": 5},
            {"id": ids[1], "name": "D", "age": 6},
        ],
        id_=3,
    )
    assert resp.status_code == 200
    resp = await rpc(
        "Gadget.bulk_merge",
        [
            {"id": ids[0], "name": "E", "age": 7},
            {"id": ids[1], "age": 8},
        ],
        id_=4,
    )
    assert resp.status_code == 200
    merged = resp.json()["result"]
    assert merged[0]["id"] == ids[0]
    assert merged[0]["name"] == "E"

    resp = await rpc("Gadget.bulk_delete", ids + [str(uuid4())], id_=5)
    assert resp.status_code == 200
    assert resp.json()["result"]["deleted"] == 2
