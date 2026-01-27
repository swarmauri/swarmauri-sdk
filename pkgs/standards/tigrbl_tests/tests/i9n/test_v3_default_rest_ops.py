import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from tigrbl.types import App, Integer, Mapped, String

from tigrbl import TigrblApp as Tigrblv3
from tigrbl.engine.shortcuts import mem
from tigrbl.specs import F, IO, S, acol
from tigrbl.orm.tables import Base as Base3


@pytest_asyncio.fixture()
async def client_and_model():
    Base3.metadata.clear()

    class Gadget(Base3):
        __tablename__ = "gadgets"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True),
            io=IO(out_verbs=("read", "list")),
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
    # TigrblApp/Tigrbl dropped the ``get_db`` attribute in favor of using the
    # engine facade. Using an async SQLite engine in this test triggers a
    # ``MissingGreenlet`` error when SQLAlchemy performs I/O. Configure a
    # synchronous in-memory engine instead so the REST operations run without
    # requiring greenlet magic.
    api = Tigrblv3(engine=mem(async_=False))
    api.include_model(Gadget, prefix="")
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
async def test_rest_create(client_and_model):
    client, _ = client_and_model
    resp = await client.post("/gadget", json={"name": "A", "age": 1})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "A"
    assert data["age"] == 1


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rest_read(client_and_model):
    client, _ = client_and_model
    created = await client.post("/gadget", json={"name": "A", "age": 1})
    item_id = created.json()["id"]
    resp = await client.get(f"/gadget/{item_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == item_id


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rest_update(client_and_model):
    client, _ = client_and_model
    created = await client.post("/gadget", json={"name": "A", "age": 1})
    item_id = created.json()["id"]
    resp = await client.patch(f"/gadget/{item_id}", json={"name": "B", "age": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "B"
    assert data["age"] == 2


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rest_replace(client_and_model):
    client, _ = client_and_model
    created = await client.post("/gadget", json={"name": "A", "age": 1})
    item_id = created.json()["id"]
    resp = await client.put(f"/gadget/{item_id}", json={"name": "C", "age": 5})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "C"
    assert data["age"] == 5


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rest_delete(client_and_model):
    client, _ = client_and_model
    created = await client.post("/gadget", json={"name": "A", "age": 1})
    item_id = created.json()["id"]
    resp = await client.delete(f"/gadget/{item_id}")
    assert resp.status_code == 200
    assert resp.json()["deleted"] == 1
    follow = await client.get(f"/gadget/{item_id}")
    assert follow.status_code == 404


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rest_list(client_and_model):
    client, _ = client_and_model
    await client.post("/gadget", json={"name": "A", "age": 1})
    await client.post("/gadget", json={"name": "B", "age": 2})
    resp = await client.get("/gadget")
    assert resp.status_code == 200
    names = {item["name"] for item in resp.json()}
    assert names == {"A", "B"}


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rest_clear(client_and_model):
    client, _ = client_and_model
    await client.post("/gadget", json={"name": "A", "age": 1})
    await client.post("/gadget", json={"name": "B", "age": 2})
    resp = await client.delete("/gadget")
    assert resp.status_code == 200
    assert resp.json()["deleted"] == 2
    remaining = await client.get("/gadget")
    assert remaining.status_code == 200
    assert remaining.json() == []
