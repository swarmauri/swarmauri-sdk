import pytest_asyncio
import pytest
from pydantic import BaseModel
from tigrbl.types import App
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, String

from tigrbl import TigrblApp, Base, op_ctx, schema_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk


@pytest_asyncio.fixture
async def widget_client():
    Base.metadata.clear()

    class Widget(Base, GUIDPk):
        __tablename__ = "widgets"
        name = Column(String, nullable=False)

        @schema_ctx(alias="Echo", kind="in")
        class EchoIn(BaseModel):
            name: str

        @schema_ctx(alias="Echo", kind="out")
        class EchoOut(BaseModel):
            name: str

        @op_ctx(
            alias="echo",
            arity="collection",
            request_schema="Echo.in",
            response_schema="Echo.out",
        )
        async def echo(cls, ctx):
            return ctx["payload"]

    app = App()
    api = TigrblApp(engine=mem())
    api.include_model(Widget, prefix="")
    api.mount_jsonrpc()
    await api.initialize()
    app.include_router(api.router)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client, api, Widget


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_ctx_binding(widget_client):
    _, _, Widget = widget_client
    assert hasattr(Widget.schemas, "Echo")
    assert Widget.schemas.Echo.in_ is Widget.EchoIn
    assert Widget.schemas.Echo.out is Widget.EchoOut


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_ctx_openapi(widget_client):
    client, _, _ = widget_client
    spec = (await client.get("/openapi.json")).json()
    paths = spec["paths"]
    assert "/widget/echo" in paths
    schemas = spec["components"]["schemas"]
    assert "EchoIn" in schemas
    assert "EchoOut" in schemas


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_ctx_rest_and_rpc(widget_client):
    client, _, _ = widget_client
    res = await client.post("/widget/echo", json={"name": "foo"})
    assert res.status_code == 200
    assert res.json() == {"name": "foo"}

    rpc_payload = {
        "jsonrpc": "2.0",
        "method": "Widget.echo",
        "params": {"name": "bar"},
        "id": 1,
    }
    res_rpc = await client.post("/rpc/", json=rpc_payload)
    assert res_rpc.status_code == 200
    assert res_rpc.json()["result"] == {"name": "bar"}
