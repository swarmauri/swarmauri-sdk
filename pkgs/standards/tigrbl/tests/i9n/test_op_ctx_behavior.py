import pytest
from httpx import ASGITransport, AsyncClient
from tigrbl.types import App, BaseModel, Column, String, UUID

from tigrbl import TigrblApp, op_ctx, schema_ctx, hook_ctx
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.runtime.kernel import build_phase_chains


# helper to set up Tigrbl with sync DB from fixture


def setup_api(model_cls, get_db):
    Base.metadata.clear()
    app = App()
    api = TigrblApp(get_db=get_db)
    api.include_model(model_cls, prefix="")
    api.initialize()
    app.include_router(api.router)
    return app, api


@pytest.mark.i9n
@pytest.mark.asyncio
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
        res = await client.post("/thing", json={"name": "a"})
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
        res = await client.post("/item", json={"name": "a"})
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
async def test_op_ctx_preserves_canon_schemas(sync_db_session):
    _, get_sync_db = sync_db_session

    class RegisterIn(BaseModel):
        name: str

    class TokenPair(BaseModel):
        access: str

    class Widget(Base, GUIDPk):
        __tablename__ = "widgets"
        __resource__ = "widget"
        name = Column(String)

        @op_ctx(
            alias="register",
            target="custom",
            arity="collection",
            request_schema=RegisterIn,
            response_schema=TokenPair,
        )
        def register(cls, ctx):
            return TokenPair(access="x")

    app, _ = setup_api(Widget, get_sync_db)
    spec = app.openapi()
    schemas = spec["components"]["schemas"].keys()
    assert "WidgetCreateRequest" in schemas
    assert "WidgetCreateResponse" in schemas
    assert "WidgetRegisterRequest" in schemas
    assert "WidgetRegisterResponse" in schemas


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
        res = await client.post("/widget", json={"name": "w"})
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
async def test_op_ctx_rest_call(sync_db_session):
    _, get_sync_db = sync_db_session

    class Gadget(Base, GUIDPk):
        __tablename__ = "gadgets"
        __resource__ = "gadget"
        name = Column(String)

        @schema_ctx(alias="Ping", kind="out")
        class PingOut(BaseModel):
            msg: str

        @op_ctx(
            alias="ping",
            target="custom",
            arity="collection",
            response_schema="Ping.out",
        )
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
    app.include_router(api.router)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        payload = {"jsonrpc": "2.0", "method": "Widget.ping", "params": {}, "id": 1}
        res = await client.post("/rpc", json=payload, follow_redirects=True)
    assert res.status_code == 200
    assert res.json()["result"] == {"ok": True}


@pytest.mark.i9n
@pytest.mark.asyncio
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
        r2 = await client.get(f"/widget/{wid}")
    assert r2.status_code == 200
    assert r2.json()["name"] == "w"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_op_ctx_hookz(sync_db_session):
    _, get_sync_db = sync_db_session
    calls = []

    class Widget(Base, GUIDPk):
        __tablename__ = "widgets"
        __resource__ = "widget"
        name = Column(String)

        @schema_ctx(alias="Echo", kind="out")
        class EchoOut(BaseModel):
            msg: str

        @op_ctx(
            alias="echo",
            target="custom",
            arity="collection",
            response_schema="Echo.out",
        )
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
    assert calls.count("hooked") >= 1


@pytest.mark.i9n
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
    assert "create" in names


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

    assert chains["START_TX"]
    assert chains["END_TX"]
