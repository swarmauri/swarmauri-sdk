from types import SimpleNamespace

import pytest
import pytest_asyncio
from autoapi.v3.types import App
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from autoapi.v3.autoapi import AutoAPI
from autoapi.v3.orm.tables import Base
from autoapi.v3.orm.mixins import GUIDPk
from autoapi.v3.specs import acol, F, IO, S
from autoapi.v3.types import String
from autoapi.v3.runtime.atoms.schema import collect_in


@pytest_asyncio.fixture
async def fs_app():
    Base.metadata.clear()
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    def get_db():
        with SessionLocal() as session:
            yield session

    class FSItem(Base, GUIDPk):
        __tablename__ = "fs_items"
        name = acol(
            storage=S(type_=String, nullable=False),
            field=F(
                constraints={"max_length": 5},
                required_in=("create",),
                allow_null_in=("update",),
            ),
            io=IO(in_verbs=("create", "update"), out_verbs=("read",)),
        )

    Base.metadata.create_all(engine)
    app = App()
    api = AutoAPI(app=app, get_db=get_db)
    api.include_model(FSItem)
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    try:
        yield client, api, SessionLocal, FSItem
    finally:
        await client.aclose()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_field_spec_openapi(fs_app):
    client, _, _, _ = fs_app
    spec = (await client.get("/openapi.json")).json()
    schema = spec["components"]["schemas"]["FSItemCreateRequest"]
    assert "name" in schema["required"]
    assert schema["properties"]["name"]["type"] == "string"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_field_spec_column_length(fs_app):
    _, _, _, FSItem = fs_app
    assert FSItem.__table__.c.name.type.length == 5


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_field_spec_rest_required(fs_app):
    client, _, _, _ = fs_app
    resp = await client.post("/fsitem", json={})
    assert resp.status_code == 422


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_field_spec_allow_null_update(fs_app):
    client, _, SessionLocal, FSItem = fs_app
    create = await client.post("/fsitem", json={"name": "ok"})
    item_id = create.json()["id"]
    upd = await client.patch(f"/fsitem/{item_id}", json={"name": None})
    assert upd.status_code == 422


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_field_spec_rpc_required(fs_app):
    _, api, SessionLocal, FSItem = fs_app
    with SessionLocal() as session:
        with pytest.raises(Exception):
            await api.rpc_call(FSItem, "create", payload={}, db=session)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_field_spec_core_crud_create(fs_app):
    _, api, SessionLocal, FSItem = fs_app
    with SessionLocal() as session:
        obj = await api.core.FSItem.create({"name": "hi"}, db=session)
        assert obj["name"] == "hi"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_field_spec_collect_in_atom(fs_app):
    _, _, _, FSItem = fs_app
    specs = FSItem.__autoapi_cols__
    ctx = SimpleNamespace(specs=specs, op="create", temp={})
    collect_in.run(None, ctx)
    schema = ctx.temp["schema_in"]
    assert schema["by_field"]["name"]["required"] is True
