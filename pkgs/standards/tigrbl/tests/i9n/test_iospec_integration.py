import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from types import SimpleNamespace

from tigrbl import TigrblApp
from tigrbl.engine import resolver as _resolver
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import IO, S, acol
from tigrbl.types import App, String, UUID
from tigrbl.core import crud
from tigrbl.runtime.atoms.resolve import assemble


class Widget(Base, GUIDPk):
    __tablename__ = "widgets"

    name = acol(
        storage=S(type_=String, nullable=False),
        io=IO(in_verbs=("create",), out_verbs=("read",)),
    )
    secret = acol(
        storage=S(type_=String, nullable=True),
        io=IO(in_verbs=("create",), out_verbs=(), allow_out=False),
    )
    created_at = acol(
        storage=S(type_=String, nullable=False),
        io=IO(in_verbs=("create",), out_verbs=("read",)),
        default_factory=lambda ctx: "now",
    )


@pytest_asyncio.fixture
async def widget_setup():
    app = App()
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(Widget, prefix="/widget")
    api.mount_jsonrpc(prefix="/rpc")
    api.attach_diagnostics(prefix="/system")
    api.initialize()
    app.include_router(api.router)

    prov = _resolver.resolve_provider()
    SessionLocal = prov.session

    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    yield client, api, SessionLocal
    await client.aclose()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_request_schema_reflects_io_spec(widget_setup):
    _, api, _ = widget_setup
    schema = api.schemas.Widget.create.in_.model_json_schema()
    assert set(schema["properties"]) == {"name", "secret", "created_at"}


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_response_schema_reflects_io_spec(widget_setup):
    _, api, _ = widget_setup
    schema = api.schemas.Widget.read.out.model_json_schema()
    assert set(schema["properties"]) == {"id", "name", "created_at", "secret"}


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_columns_store_io_spec(widget_setup):
    _, _, _ = widget_setup
    spec = Widget.__tigrbl_cols__["secret"].io
    assert spec.allow_out is False


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_default_factory_resolution(widget_setup):
    _, _, _ = widget_setup
    specs = Widget.__tigrbl_cols__
    ctx = SimpleNamespace(
        specs=specs, op="create", temp={"in_values": {}}, persist=True
    )
    assemble.run(None, ctx)
    assert ctx.temp["assembled_values"]["created_at"] == "now"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_orm_model_carries_io_spec(widget_setup):
    _, _, _ = widget_setup
    assert "name" in Widget.__tigrbl_cols__


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_openapi_reflects_io_spec(widget_setup):
    client, _, _ = widget_setup
    spec = (await client.get("/openapi.json")).json()
    props = spec["components"]["schemas"]["WidgetReadResponse"]["properties"]
    assert "secret" in props


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_persists_data(widget_setup):
    client, _, SessionLocal = widget_setup
    payload = {
        "name": "hi",
        "secret": "s",
        "created_at": "now",
    }
    resp = await client.post("/widget/widget", json=payload)
    wid = UUID(resp.json()["id"])
    with SessionLocal() as session:
        obj = session.execute(select(Widget).where(Widget.id == wid)).scalar_one()
    assert obj.name == "hi"
    assert obj.secret == "s"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rest_calls_honor_io_spec(widget_setup):
    client, _, _ = widget_setup
    payload = {
        "name": "hi",
        "secret": "s",
        "created_at": "now",
    }
    resp = await client.post("/widget/widget", json=payload)
    wid = resp.json()["id"]
    data = (await client.get(f"/widget/widget/{wid}")).json()
    assert data["secret"] == "s"
    assert data["name"] == "hi"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rpc_methods_honor_io_spec(widget_setup):
    client, _, _ = widget_setup
    payload = {
        "jsonrpc": "2.0",
        "method": "Widget.create",
        "params": {
            "name": "rpc",
            "secret": "x",
            "created_at": "now",
        },
        "id": 1,
    }
    result = (await client.post("/rpc/", json=payload)).json()["result"]
    assert result["secret"] == "x"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_core_crud_binding(widget_setup):
    _, _, _ = widget_setup
    assert Widget.hooks.create.HANDLER[0].__qualname__ == crud.create.__qualname__


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hookz_reports_operations(widget_setup):
    client, _, _ = widget_setup
    data = (await client.get("/system/hookz")).json()
    assert "Widget" in data
    assert "create" in data["Widget"]


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_kernelz_lists_atoms_and_steps(widget_setup):
    client, _, _ = widget_setup
    data = (await client.get("/system/kernelz")).json()
    steps = data["Widget"]["create"]
    assert "HANDLER:hook:wire:tigrbl:core:crud:ops:create@HANDLER" in steps
    assert any("hook:sys:txn:begin@START_TX" in s for s in steps)
