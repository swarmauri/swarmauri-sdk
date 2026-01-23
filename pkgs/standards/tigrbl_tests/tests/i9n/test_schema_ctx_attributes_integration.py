import pytest
import pytest_asyncio

from httpx import ASGITransport, AsyncClient

from tigrbl.types import App, BaseModel, Column, Integer, String

from tigrbl import TigrblApp, Base, schema_ctx
from tigrbl.core import crud
from tigrbl.engine.shortcuts import mem
from tigrbl.engine import resolver as _resolver


@pytest_asyncio.fixture
async def schema_ctx_client():
    Base.metadata.clear()

    class Widget(Base):
        __tablename__ = "widgets"
        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String, nullable=False)
        age = Column(Integer, nullable=False, default=5)

        @schema_ctx(alias="create", kind="in")
        class CreateSchema(BaseModel):
            name: str

        @schema_ctx(alias="read", kind="out")
        class ReadSchema(BaseModel):
            id: int
            name: str
            age: int

    cfg = mem()
    app = App()
    api = TigrblApp(engine=cfg)
    api.include_model(Widget, prefix="")
    api.mount_jsonrpc()
    api.attach_diagnostics()
    await api.initialize()
    prov = _resolver.resolve_provider()
    _, sessionmaker = prov.ensure()
    app.include_router(api.router)

    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    return client, api, Widget, sessionmaker


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_ctx_bindings(schema_ctx_client):
    _, _, Widget, _ = schema_ctx_client
    assert hasattr(Widget.schemas, "create")
    assert Widget.schemas.create.in_ is Widget.CreateSchema
    assert Widget.schemas.read.out is Widget.ReadSchema


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_ctx_request_response_schema(schema_ctx_client):
    _, api, _, _ = schema_ctx_client
    create_schema = api.schemas.Widget.create.in_
    read_schema = api.schemas.Widget.read.out
    assert create_schema.model_fields["name"].is_required()
    assert "age" in read_schema.model_fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_ctx_columns(schema_ctx_client):
    _, _, Widget, _ = schema_ctx_client
    table = Widget.__table__
    assert table.c.name.nullable is False
    assert table.c.age.default.arg == 5


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_ctx_default_resolution(schema_ctx_client):
    client, _, _, _ = schema_ctx_client
    resp = await client.post("/widget", json={"name": "A"})
    assert resp.status_code == 201
    assert resp.json()["age"] == 5


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_ctx_internal_orm(schema_ctx_client):
    _, api, Widget, _ = schema_ctx_client
    assert api.models["Widget"] is Widget
    assert "age" in api.columns["Widget"]


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_ctx_openapi(schema_ctx_client):
    client, _, _, _ = schema_ctx_client
    spec = (await client.get("/openapi.json")).json()
    schemas = spec["components"]["schemas"]
    assert "CreateSchema" in schemas
    assert "ReadSchema" in schemas


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_ctx_storage_sqlalchemy(schema_ctx_client):
    client, _, Widget, sessionmaker = schema_ctx_client
    resp = await client.post("/widget", json={"name": "B"})
    item_id = resp.json()["id"]
    async with sessionmaker() as session:
        obj = await session.get(Widget, item_id)
        assert obj is not None
        assert isinstance(Widget.__table__.c.name.type, String)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_ctx_rest_calls(schema_ctx_client):
    client, _, _, _ = schema_ctx_client
    resp = await client.post("/widget", json={"name": "C"})
    item_id = resp.json()["id"]
    read = await client.get(f"/widget/{item_id}")
    assert read.status_code == 200
    assert read.json()["id"] == item_id


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_ctx_rpc_methods(schema_ctx_client):
    client, _, _, _ = schema_ctx_client
    payload = {"name": "rpc"}
    resp = await client.post(
        "/rpc/",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "Widget.create",
            "params": payload,
        },
    )
    assert resp.json()["result"]["name"] == "rpc"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_ctx_core_crud(schema_ctx_client):
    _, _, Widget, sessionmaker = schema_ctx_client
    async with sessionmaker() as session:
        obj = await crud.create(Widget, {"name": "core"}, db=session)
        await session.commit()
    assert obj.age == 5


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_ctx_hookz(schema_ctx_client):
    client, _, _, _ = schema_ctx_client
    hooks = (await client.get("/system/hookz")).json()
    assert "Widget" in hooks
    assert "create" in hooks["Widget"]


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_ctx_atomz(schema_ctx_client):
    client, _, _, _ = schema_ctx_client
    kernelz = (await client.get("/system/kernelz")).json()
    steps = kernelz["Widget"]["create"]
    assert "HANDLER:hook:wire:tigrbl:core:crud:ops:create@HANDLER" in steps


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_ctx_system_steps(schema_ctx_client):
    client, _, _, _ = schema_ctx_client
    kernelz = (await client.get("/system/kernelz")).json()
    assert "Widget" in kernelz
    assert "create" in kernelz["Widget"]
