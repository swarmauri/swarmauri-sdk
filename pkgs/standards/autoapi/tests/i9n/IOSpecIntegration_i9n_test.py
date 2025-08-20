"""Integration tests for AutoAPI v3 IOSpec attributes."""

from __future__ import annotations

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Mapped

from autoapi.v3 import AutoAPI, OpSpec, include_model
from autoapi.v3.decorators import hook_ctx
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.specs import IO, F, S, acol, vcol
from autoapi.v3.tables import Base
from autoapi.v3.types import Integer, String


@pytest_asyncio.fixture
async def v3_client():
    """Create a FastAPI app with a single model using IoSpec."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    SessionLocal = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async def get_async_db():
        async with SessionLocal() as session:
            yield session

    app = FastAPI()
    api = AutoAPI(app=app, get_async_db=get_async_db)

    class Thing(Base, GUIDPk):
        """Model with IoSpec-driven attributes."""

        __tablename__ = "things"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True),
            io=IO(out_verbs=("read",)),
        )
        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            io=IO(
                in_verbs=("create",),
                out_verbs=("read",),
                alias_in="first_name",
                alias_out="firstName",
                default_factory=lambda ctx: "anon",
                filter_ops=("eq",),
                sortable=True,
            ),
        )
        nickname: str = vcol(
            field=F(py_type=str),
            io=IO(out_verbs=("read",)),
        )

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        async def flag(cls, ctx):
            ctx.temp["hook"] = True

    ops = [
        OpSpec(alias="create", target="create"),
        OpSpec(alias="read", target="read"),
        OpSpec(alias="list", target="list"),
    ]
    include_model(api, Thing, opspecs=ops)
    await api.initialize_async()
    api.mount_jsonrpc(prefix="/rpc")
    api.attach_diagnostics(prefix="/system")

    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")

    try:
        yield client, api, Thing, SessionLocal
    finally:
        await client.aclose()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_request_and_response_schemas(v3_client):
    """Request and response schemas expose IoSpec aliases."""
    _, api, Thing, _ = v3_client
    create_schema = api.schemas.ThingCreateIn
    read_schema = api.schemas.ThingReadOut
    assert create_schema.model_fields["name"].alias == "first_name"
    assert read_schema.model_fields["name"].serialization_alias == "firstName"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_columns_materialized(v3_client):
    """IoSpec-backed columns appear in model metadata."""
    _, api, Thing, _ = v3_client
    cols = api.columns["Thing"]
    assert "id" in cols and "name" in cols


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_default_value_resolution(v3_client):
    """Default factory resolves missing values during create."""
    _, api, Thing, SessionLocal = v3_client
    async with SessionLocal() as session:
        obj = await api.core.Thing.create({}, db=session)
        assert obj.name == "anon"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_internal_model_bindings(v3_client):
    """Binding attaches internal namespaces to model."""
    _, api, Thing, _ = v3_client
    assert hasattr(Thing, "__autoapi_cols__")
    assert hasattr(Thing, "schemas")


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_openapi_reflects_iospec(v3_client):
    """OpenAPI includes IoSpec-driven aliases."""
    client, _, _, _ = v3_client
    spec = (await client.get("/openapi.json")).json()
    create_props = spec["components"]["schemas"]["ThingCreate"]["properties"]
    assert "first_name" in create_props
    assert "id" not in create_props


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_virtual_column_not_materialized(v3_client):
    """Virtual columns are not persisted in storage."""
    _, _, Thing, _ = v3_client
    assert "nickname" not in Thing.__table__.c


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rest_calls_use_alias(v3_client):
    """REST endpoints honor IoSpec aliases."""
    client, _, _, _ = v3_client
    resp = await client.post("/Thing", json={"first_name": "Jane"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["firstName"] == "Jane"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rpc_method_respects_alias(v3_client):
    """JSON-RPC calls use IoSpec aliases."""
    client, _, _, _ = v3_client
    payload = {
        "jsonrpc": "2.0",
        "method": "Thing.create",
        "params": {"first_name": "Jane"},
        "id": 1,
    }
    resp = await client.post("/rpc", json=payload)
    result = resp.json()["result"]
    assert result["firstName"] == "Jane"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_core_crud_filters_inbound(v3_client):
    """Core CRUD ignores disallowed fields."""
    _, api, Thing, SessionLocal = v3_client
    async with SessionLocal() as session:
        obj = await api.core.Thing.create({"id": 99, "name": "Jane"}, db=session)
        assert obj.id != 99


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hookz_reports_hooks(v3_client):
    """Diagnostics endpoint reports model hooks."""
    client, _, _, _ = v3_client
    data = (await client.get("/system/hookz")).json()
    assert "Thing" in data
    assert "create" in data["Thing"]


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_planz_lists_atoms(v3_client):
    """Diagnostics plan includes runtime atoms."""
    client, _, _, _ = v3_client
    plans = (await client.get("/system/planz")).json()
    steps = plans["Thing"]["create"]
    assert any("collect_in" in step for step in steps)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_planz_has_create_and_read_steps(v3_client):
    """Diagnostics plan exposes system step sequences."""
    client, _, _, _ = v3_client
    plans = (await client.get("/system/planz")).json()
    assert "create" in plans["Thing"]
    assert "read" in plans["Thing"]
