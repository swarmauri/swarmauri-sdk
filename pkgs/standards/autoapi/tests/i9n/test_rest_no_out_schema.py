import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Mapped
from sqlalchemy import Integer, String

from autoapi.v3.autoapi import AutoAPI as AutoAPIv3
from autoapi.v3.specs import IO, S, acol
from autoapi.v3.tables import Base as Base3


@pytest_asyncio.fixture()
async def client_and_model():
    Base3.metadata.clear()

    class Widget(Base3):
        __tablename__ = "widgets"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True)
        )
        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            io=IO(in_verbs=("create", "update", "replace")),
        )

        __autoapi_cols__ = {"id": id, "name": name}

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
    api.include_model(Widget, prefix="")
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    try:
        yield client, Widget
    finally:
        await client.aclose()
        await engine.dispose()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rest_read_and_list_without_out_schema(client_and_model):
    client, _ = client_and_model
    created = await client.post("/widget", json={"name": "A"})
    item_id = created.json()["id"]

    read_resp = await client.get(f"/widget/{item_id}")
    assert read_resp.status_code == 200
    assert read_resp.json()["name"] == "A"

    list_resp = await client.get("/widget")
    assert list_resp.status_code == 200
    assert list_resp.json()[0]["id"] == item_id
