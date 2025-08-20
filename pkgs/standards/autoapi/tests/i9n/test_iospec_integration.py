import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from types import SimpleNamespace
import uuid

from autoapi.v3.autoapi import AutoAPI
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.specs import IO, S, acol
from autoapi.v3.types import String
from autoapi.v3.core import crud
from autoapi.v3.runtime.atoms.resolve import assemble


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
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    def get_db():
        with SessionLocal() as session:
            yield session

    Base.metadata.create_all(engine)

    app = FastAPI()
    api = AutoAPI(app=app, get_db=get_db)
    api.include_model(Widget, prefix="/widget")
    api.mount_jsonrpc(prefix="/rpc")
    api.attach_diagnostics(prefix="/system")

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
    info = Widget.__table__.c.secret.info["autoapi"]["spec"].io
    assert info.allow_out is False


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_default_factory_resolution(widget_setup):
    _, _, _ = widget_setup
    specs = Widget.__autoapi_cols__
    ctx = SimpleNamespace(
        specs=specs, op="create", temp={"in_values": {}}, persist=True
    )
    assemble.run(None, ctx)
    assert ctx.temp["assembled_values"]["created_at"] == "now"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_orm_model_carries_io_spec(widget_setup):
    _, _, _ = widget_setup
    assert "name" in Widget.__autoapi_cols__


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_openapi_reflects_io_spec(widget_setup):
    client, _, _ = widget_setup
    spec = (await client.get("/openapi.json")).json()
    props = spec["components"]["schemas"]["WidgetRead"]["properties"]
    assert "secret" in props


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_persists_data(widget_setup):
    client, _, SessionLocal = widget_setup
    resp = await client.post(
        "/widget/widget", json={"name": "hi", "secret": "s", "created_at": "now"}
    )
    wid = uuid.UUID(resp.json()["id"])
    with SessionLocal() as session:
        obj = session.execute(select(Widget).where(Widget.id == wid)).scalar_one()
    assert obj.name == "hi"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rest_calls_honor_io_spec(widget_setup):
    client, _, _ = widget_setup
    resp = await client.post(
        "/widget/widget", json={"name": "hi", "secret": "s", "created_at": "now"}
    )
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
        "params": {"name": "rpc", "secret": "x", "created_at": "now"},
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
async def test_planz_lists_atoms_and_steps(widget_setup):
    client, _, _ = widget_setup
    data = (await client.get("/system/planz")).json()
    steps = data["Widget"]["create"]
    assert any("crud.create" in s for s in steps)
    assert any("start_tx" in s for s in steps)
