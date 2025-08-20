import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel
from sqlalchemy import Column, String
from uuid import UUID

from autoapi.v3 import AutoAPI, op_ctx, schema_ctx, hook_ctx
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.runtime.kernel import build_phase_chains


# helper to set up AutoAPI with sync DB from fixture


def setup_api(model_cls, get_db):
    Base.metadata.clear()
    app = FastAPI()
    api = AutoAPI(app=app, get_db=get_db)
    api.include_model(model_cls, prefix="")
    api.initialize_sync()
    return app, api


@pytest.mark.i9n
@pytest.mark.asyncio
@pytest.mark.xfail(reason="request schema coercion pending")
async def test_op_ctx_request_response_schemas(sync_db_session):
    _, get_sync_db = sync_db_session

    class Widget(Base, GUIDPk):
        __tablename__ = "widgets"
        __resource__ = "widget"
        name = Column(String)

        @schema_ctx(alias="Echo", kind="in")
        class EchoIn(BaseModel):
            text: str

        @schema_ctx(alias="Echo", kind="out")
        class EchoOut(BaseModel):
            text: str

        @op_ctx(
            alias="echo",
            target="custom",
            arity="collection",
            request_schema="Echo.in",
            response_schema="Echo.out",
        )
        def echo(cls, ctx):
            payload = ctx.get("payload") or {}
            return {"text": str(payload.get("text"))}

    app, api = setup_api(Widget, get_sync_db)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.post("/widget/echo", json={"text": "123"})
    assert res.status_code == 200
    assert res.json() == {"text": "123"}


@pytest.mark.i9n
def test_op_ctx_columns(sync_db_session):
    _, get_sync_db = sync_db_session

    class Gadget(Base, GUIDPk):
        __tablename__ = "gadgets"
        __resource__ = "gadget"
        name = Column(String)
        flag = Column(String)

        @op_ctx(alias="ping", target="custom", arity="collection")
        def ping(cls, ctx):
            return {}

    _, api = setup_api(Gadget, get_sync_db)
    assert set(api.columns["Gadget"]) == {"id", "name", "flag"}


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_op_ctx_defaults_value_resolution(sync_db_session):
    _, get_sync_db = sync_db_session

    class Thing(Base, GUIDPk):
        __tablename__ = "things"
        __resource__ = "thing"
        name = Column(String)
        status = Column(String, default="new")

        @op_ctx(alias="make", target="create")
        def make(cls, ctx):
            pass

    app, api = setup_api(Thing, get_sync_db)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.post("/thing/make", json={"name": "a"})
    assert res.status_code == 201
    item_id = UUID(res.json()["id"])
    assert res.json()["status"] == "new"

    gen = get_sync_db()
    session = next(gen)
    obj = session.get(Thing, item_id)
    assert obj.status == "new"
    try:
        next(gen)
    except StopIteration:
        pass


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_op_ctx_internal_orm_models(sync_db_session):
    _, get_sync_db = sync_db_session

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        __resource__ = "item"
        name = Column(String)

        @op_ctx(alias="seed", target="create")
        def seed(cls, ctx):
            pass

    app, api = setup_api(Item, get_sync_db)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.post("/item/seed", json={"name": "a"})
    assert res.status_code == 201
    item_id = UUID(res.json()["id"])

    assert api.models["Item"] is Item
    gen = get_sync_db()
    session = next(gen)
    assert isinstance(session.get(Item, item_id), Item)
    try:
        next(gen)
    except StopIteration:
        pass


@pytest.mark.i9n
def test_op_ctx_openapi_json(sync_db_session):
    _, get_sync_db = sync_db_session

    class Widget(Base, GUIDPk):
        __tablename__ = "widgets"
        __resource__ = "widget"
        name = Column(String)

        @op_ctx(alias="ping", target="custom", arity="collection")
        def ping(cls, ctx):
            return {}

    app, _ = setup_api(Widget, get_sync_db)
    spec = app.openapi()
    assert "/widget/ping" in spec["paths"]
    assert "post" in spec["paths"]["/widget/ping"]


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_op_ctx_storage_sqlalchemy(sync_db_session):
    _, get_sync_db = sync_db_session

    class Widget(Base, GUIDPk):
        __tablename__ = "widgets"
        __resource__ = "widget"
        name = Column(String)

        @op_ctx(alias="make", target="create")
        def make(cls, ctx):
            pass

    app, _ = setup_api(Widget, get_sync_db)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.post("/widget/make", json={"name": "w"})
    assert res.status_code == 201
    item_id = UUID(res.json()["id"])

    gen = get_sync_db()
    session = next(gen)
    obj = session.get(Widget, item_id)
    assert obj is not None
    try:
        next(gen)
    except StopIteration:
        pass


@pytest.mark.i9n
@pytest.mark.asyncio
@pytest.mark.xfail(reason="custom op dispatch error")
async def test_op_ctx_rest_call(sync_db_session):
    _, get_sync_db = sync_db_session

    class Gadget(Base, GUIDPk):
        __tablename__ = "gadgets"
        __resource__ = "gadget"
        name = Column(String)

        @op_ctx(alias="ping", target="custom", arity="collection")
        def ping(cls, ctx):
            return {"msg": "ok"}

    app, _ = setup_api(Gadget, get_sync_db)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.post("/gadget/ping", json={})
    assert res.status_code == 200
    assert res.json() == {"msg": "ok"}


@pytest.mark.i9n
@pytest.mark.asyncio
@pytest.mark.xfail(reason="rpc dispatch error")
async def test_op_ctx_rpc_method(sync_db_session):
    _, get_sync_db = sync_db_session

    class Widget(Base, GUIDPk):
        __tablename__ = "widgets"
        __resource__ = "widget"
        name = Column(String)

        @op_ctx(alias="ping", target="custom", arity="collection")
        def ping(cls, ctx):
            return {"ok": True}

    app, api = setup_api(Widget, get_sync_db)
    api.mount_jsonrpc(prefix="/rpc")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        payload = {"jsonrpc": "2.0", "method": "Widget.ping", "params": {}, "id": 1}
        res = await client.post("/rpc", json=payload, follow_redirects=True)
    assert res.status_code == 200
    assert res.json()["result"] == {"ok": True}


@pytest.mark.i9n
@pytest.mark.asyncio
@pytest.mark.xfail(reason="alias routing error")
async def test_op_ctx_core_crud(sync_db_session):
    _, get_sync_db = sync_db_session

    class Widget(Base, GUIDPk):
        __tablename__ = "widgets"
        __resource__ = "widget"
        name = Column(String)

        @op_ctx(alias="fetch", target="read", arity="member")
        def fetch(cls, ctx, obj):
            return obj

    app, _ = setup_api(Widget, get_sync_db)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        r1 = await client.post("/widget", json={"name": "w"})
        wid = UUID(r1.json()["id"])  # capture id as UUID
        r2 = await client.get(f"/widget/{wid}/fetch")
    assert r2.status_code == 200
    assert r2.json()["name"] == "w"


@pytest.mark.i9n
@pytest.mark.asyncio
@pytest.mark.xfail(reason="hook execution error")
async def test_op_ctx_hookz(sync_db_session):
    _, get_sync_db = sync_db_session
    calls = []

    class Widget(Base, GUIDPk):
        __tablename__ = "widgets"
        __resource__ = "widget"
        name = Column(String)

        @op_ctx(alias="echo", target="custom", arity="collection")
        def echo(cls, ctx):
            return {"msg": "hi"}

        @hook_ctx(ops="echo", phase="POST_HANDLER")
        async def record(cls, ctx):
            calls.append("hooked")

    app, _ = setup_api(Widget, get_sync_db)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post("/widget/echo", json={})
    assert calls == ["hooked"]


@pytest.mark.i9n
@pytest.mark.xfail(reason="atom injection pending")
def test_op_ctx_atom_plan(sync_db_session):
    _, get_sync_db = sync_db_session

    class Widget(Base, GUIDPk):
        __tablename__ = "widgets"
        __resource__ = "widget"
        name = Column(String)

        @op_ctx(alias="make", target="create")
        def make(cls, ctx):
            pass

    _, api = setup_api(Widget, get_sync_db)
    chains = build_phase_chains(Widget, "make")
    names = [fn.__name__ for funcs in chains.values() for fn in funcs]
    assert any(name == "validate_in" for name in names)


@pytest.mark.i9n
def test_op_ctx_system_steps(sync_db_session):
    _, get_sync_db = sync_db_session

    class Widget(Base, GUIDPk):
        __tablename__ = "widgets"
        __resource__ = "widget"
        name = Column(String)

        @op_ctx(alias="ping", target="custom", arity="collection")
        def ping(cls, ctx):
            return {}

    _, api = setup_api(Widget, get_sync_db)
    chains = build_phase_chains(Widget, "ping")
    assert any(fn.__name__ == "start_tx" for fn in chains["START_TX"])
    assert any(fn.__name__ == "end_tx" for fn in chains["END_TX"])
