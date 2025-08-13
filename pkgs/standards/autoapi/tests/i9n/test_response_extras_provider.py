import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from autoapi.v2 import AutoAPI, Base
from autoapi.v2.types import Column, String, ResponseExtrasProvider
from autoapi.v2.mixins import GUIDPk


class Widget(Base, GUIDPk, ResponseExtrasProvider):
    __tablename__ = "widgets"
    __abstract__ = False

    name = Column(String, nullable=False)

    __autoapi_response_extras__ = {"create": lambda ctx, res: {"greeting": "hi"}}


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_response_extras_are_injected(sync_db_session):
    _, get_sync_db = sync_db_session
    Base.metadata.clear()
    api = AutoAPI(base=Base, include={Widget}, get_db=get_sync_db)
    api.initialize_sync()

    app = FastAPI()
    app.include_router(api.router)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/widget", json={"name": "w1"})

    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "w1"
    assert data["greeting"] == "hi"
