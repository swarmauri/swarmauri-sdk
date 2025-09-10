import pytest
import pytest_asyncio
from typing import Iterator
from tigrbl.types import App
from httpx import AsyncClient, ASGITransport

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk, BulkCapable, Replaceable
from tigrbl.types import Column, String

pytestmark = pytest.mark.skip("bulk rest endpoints require revision")


@pytest_asyncio.fixture()
async def v3_client() -> Iterator[tuple[AsyncClient, type]]:
    Base.metadata.clear()

    class Widget(Base, GUIDPk, BulkCapable, Replaceable):
        __tablename__ = "widgets"
        name = Column(String, nullable=False)
        description = Column(String, nullable=True)

    app = App()
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(Widget)
    api.initialize()
    app.include_router(api.router)

    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    try:
        yield client, Widget
    finally:
        await client.aclose()


@pytest.mark.asyncio()
async def test_bulk_create(v3_client) -> None:
    client, _ = v3_client
    payload = [
        {"name": "w1", "description": "a"},
        {"name": "w2", "description": "b"},
    ]
    res = await client.post("/widget", json=payload)
    assert res.status_code in {200, 201}
    listed = (await client.get("/widget")).json()
    assert len(listed) == 2
    assert all("id" in row for row in listed)


@pytest.mark.asyncio()
async def test_bulk_update(v3_client) -> None:
    client, _ = v3_client
    create_payload = [
        {"name": "w1", "description": "a"},
        {"name": "w2", "description": "b"},
    ]
    await client.post("/widget", json=create_payload)
    listed = (await client.get("/widget")).json()
    ids = [row["id"] for row in listed]

    update_payload = [
        {"id": ids[0], "name": "w1-updated"},
        {"id": ids[1], "description": "b2"},
    ]
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
    create_payload = [
        {"name": "w1", "description": "a"},
        {"name": "w2", "description": "b"},
    ]
    await client.post("/widget", json=create_payload)
    listed = (await client.get("/widget")).json()
    ids = [row["id"] for row in listed]

    replace_payload = [
        {"id": ids[0], "name": "w1-replaced"},
        {"id": ids[1], "name": "w2-replaced", "description": "new"},
    ]
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
    create_payload = [
        {"name": "w1", "description": "a"},
        {"name": "w2", "description": "b"},
    ]
    await client.post("/widget", json=create_payload)
    listed = (await client.get("/widget")).json()
    ids = [row["id"] for row in listed]

    res = await client.request("DELETE", "/widget", json={"ids": ids})
    assert res.status_code == 200
    assert res.json() == {"deleted": 2}

    # verify items are gone
    listed = (await client.get("/widget")).json()
    assert listed == []
