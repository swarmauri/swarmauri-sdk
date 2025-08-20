import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
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
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    try:
        yield client, Gadget
    finally:
        await client.aclose()
        await engine.dispose()


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
