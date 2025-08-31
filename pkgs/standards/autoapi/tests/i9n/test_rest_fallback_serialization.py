import pytest
import pytest_asyncio
from autoapi.v3.types import App
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Mapped

from autoapi.v3.autoapi import AutoAPI as AutoAPIv3
from autoapi.v3.specs import F, IO, S, acol
from autoapi.v3.orm.tables import Base as Base3


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
            field=F(required_in=("create",)),
            io=IO(in_verbs=("create", "update")),
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

    app = App()
    api = AutoAPIv3(app=app, get_async_db=get_async_db)
    api.include_model(Widget, prefix="")
    # Remove output schemas to trigger fallback serialization
    Widget.schemas.read.out = None
    Widget.schemas.list.out = None

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

    resp = await client.get(f"/widget/{item_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == item_id

    resp_list = await client.get("/widget")
    assert resp_list.status_code == 200
    data = resp_list.json()
    assert isinstance(data, list)
    assert data[0]["id"] == item_id
