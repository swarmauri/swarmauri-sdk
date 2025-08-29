import pytest
import pytest_asyncio
from typing import Iterator
from autoapi.v3.types import App
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from autoapi.v3.autoapi import AutoAPI
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk, BulkCapable
from autoapi.v3.types import Column, Session, String


@pytest_asyncio.fixture()
async def v3_client() -> Iterator[tuple[AsyncClient, type]]:
    Base.metadata.clear()

    class Widget(Base, GUIDPk, BulkCapable):
        __tablename__ = "widgets"
        name = Column(String, nullable=False)
        description = Column(String, nullable=True)

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    def get_db() -> Iterator[Session]:
        with SessionLocal() as session:
            yield session

    app = App()
    api = AutoAPI(app=app, get_db=get_db)
    api.include_model(Widget)

    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    try:
        yield client, Widget
    finally:
        await client.aclose()


@pytest.mark.asyncio()
async def test_bulk_create(v3_client) -> None:
    client, _ = v3_client
    payload = {
        "rows": [
            {"name": "w1", "description": "a"},
            {"name": "w2", "description": "b"},
        ]
    }
    res = await client.post("/widget", json=payload)
    assert res.status_code == 200
    listed = (await client.get("/widget")).json()
    assert len(listed) == 2
    assert all("id" in row for row in listed)


@pytest.mark.asyncio()
async def test_bulk_update(v3_client) -> None:
    client, _ = v3_client
    create_payload = {
        "rows": [
            {"name": "w1", "description": "a"},
            {"name": "w2", "description": "b"},
        ]
    }
    await client.post("/widget", json=create_payload)
    listed = (await client.get("/widget")).json()
    ids = [row["id"] for row in listed]

    update_payload = {
        "rows": [
            {"id": ids[0], "name": "w1-updated"},
            {"id": ids[1], "description": "b2"},
        ]
    }
    res = await client.patch("/widget", json=update_payload)
    assert res.status_code == 200
    data = (await client.get("/widget")).json()
    data_map = {row["id"]: row for row in data}
    assert data_map[ids[0]]["name"] == "w1-updated"
    assert data_map[ids[0]]["description"] == "a"
    assert data_map[ids[1]]["name"] == "w2"
    assert data_map[ids[1]]["description"] == "b2"


@pytest.mark.asyncio()
async def test_bulk_replace(v3_client) -> None:
    client, _ = v3_client
    create_payload = {
        "rows": [
            {"name": "w1", "description": "a"},
            {"name": "w2", "description": "b"},
        ]
    }
    await client.post("/widget", json=create_payload)
    listed = (await client.get("/widget")).json()
    ids = [row["id"] for row in listed]

    replace_payload = {
        "rows": [
            {"id": ids[0], "name": "w1-replaced"},
            {"id": ids[1], "name": "w2-replaced", "description": "new"},
        ]
    }
    res = await client.put("/widget", json=replace_payload)
    assert res.status_code == 200
    data = (await client.get("/widget")).json()
    data_map = {row["id"]: row for row in data}
    assert data_map[ids[0]]["name"] == "w1-replaced"
    # Some serializers omit null fields; treat missing as None for assertions.
    assert data_map[ids[0]].get("description") is None
    assert data_map[ids[1]]["name"] == "w2-replaced"
    assert data_map[ids[1]]["description"] == "new"


@pytest.mark.asyncio()
async def test_bulk_delete(v3_client) -> None:
    client, _ = v3_client
    create_payload = {
        "rows": [
            {"name": "w1", "description": "a"},
            {"name": "w2", "description": "b"},
        ]
    }
    await client.post("/widget", json=create_payload)
    listed = (await client.get("/widget")).json()
    ids = [row["id"] for row in listed]

    res = await client.request("DELETE", "/widget", json={"ids": ids})
    assert res.status_code == 200
    assert res.json() == {"deleted": 2}

    # verify items are gone
    listed = (await client.get("/widget")).json()
    assert listed == []
