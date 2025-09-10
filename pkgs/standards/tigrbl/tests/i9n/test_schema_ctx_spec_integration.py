import pytest
import pytest_asyncio
from tigrbl.types import App
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped

from tigrbl import TigrblApp as Tigrblv3
from tigrbl.engine import resolver as _resolver
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.tables import Base as Base3
from tigrbl.specs import F, IO, S, acol
from tigrbl.column.storage_spec import StorageTransform
from tigrbl.schema.decorators import schema_ctx
from tigrbl.core import crud


@pytest_asyncio.fixture
async def schema_ctx_client():
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
            io=IO(in_verbs=("create", "update"), out_verbs=("read", "list")),
        )
        age: Mapped[int] = acol(
            storage=S(type_=Integer, nullable=False, default=5),
            io=IO(in_verbs=("create", "update"), out_verbs=("read", "list")),
        )
        secret: Mapped[str] = acol(
            storage=S(
                type_=String,
                nullable=False,
                transform=StorageTransform(to_stored=lambda v, ctx: v.upper()),
            ),
            field=F(required_in=("create",)),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

        @schema_ctx(alias="create", kind="in")
        class Create(BaseModel):
            name: str
            secret: str

        @schema_ctx(alias="read", kind="out")
        class Read(BaseModel):
            id: int
            name: str
            age: int
            secret: str

        __tigrbl_cols__ = {
            "id": id,
            "name": name,
            "age": age,
            "secret": secret,
        }

    app = App()
    api = Tigrblv3(engine=mem(async_=False))
    api.include_model(Widget, prefix="")
    api.mount_jsonrpc()
    api.attach_diagnostics()
    api.initialize()
    prov = _resolver.resolve_provider()
    _, SessionLocal = prov.ensure()
    app.include_router(api.router)
    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    return client, api, Widget, SessionLocal


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_ctx_binding(schema_ctx_client):
    _, api, Widget, _ = schema_ctx_client
    assert api.schemas.Widget.create.in_ is Widget.Create
    assert api.schemas.Widget.read.out is Widget.Read


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_ctx_request_response_schema(schema_ctx_client):
    _, api, _, _ = schema_ctx_client
    create_schema = api.schemas.Widget.create.in_
    read_schema = api.schemas.Widget.read.out
    assert "secret" in create_schema.model_fields
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
    resp = await client.post("/widget", json={"name": "A", "secret": "s"})
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
    components = spec["components"]["schemas"]
    assert "Create" in components
    assert "Read" in components


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_ctx_storage_sqlalchemy(schema_ctx_client):
    client, _, Widget, SessionLocal = schema_ctx_client
    resp = await client.post("/widget", json={"name": "B", "secret": "abc"})
    item_id = resp.json()["id"]
    with SessionLocal() as session:
        obj = session.get(Widget, item_id)
        assert obj is not None
        assert isinstance(Widget.__table__.c.name.type, String)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_ctx_rest_calls(schema_ctx_client):
    client, _, _, _ = schema_ctx_client
    resp = await client.post("/widget", json={"name": "C", "secret": "xyz"})
    item_id = resp.json()["id"]
    read = await client.get(f"/widget/{item_id}")
    assert read.status_code == 200
    assert read.json()["id"] == item_id


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_ctx_rpc_methods(schema_ctx_client):
    client, _, _, _ = schema_ctx_client
    payload = {"name": "rpc", "secret": "mno"}
    res = await client.post(
        "/rpc/",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "Widget.create",
            "params": payload,
        },
    )
    assert res.json()["result"]["name"] == "rpc"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_ctx_core_crud(schema_ctx_client):
    _, api, Widget, SessionLocal = schema_ctx_client
    with SessionLocal() as session:
        obj = await crud.create(Widget, {"name": "core", "secret": "def"}, db=session)
        session.commit()
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
