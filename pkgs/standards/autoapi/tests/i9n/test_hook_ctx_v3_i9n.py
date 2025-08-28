import pytest
from autoapi.v3.types import App
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

from autoapi.v3.autoapi import AutoAPI
from autoapi.v3.types import Column, String
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.decorators import hook_ctx


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def create_client(model_cls):
    """Build a FastAPI app with AutoAPI v3 and return an AsyncClient."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    def get_db():
        with SessionLocal() as session:
            yield session

    app = App()
    api = AutoAPI(app=app, get_db=get_db)
    api.include_model(model_cls)
    api.mount_jsonrpc()
    api.attach_diagnostics()
    Base.metadata.create_all(engine)
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    return client, api, SessionLocal, engine


# ---------------------------------------------------------------------------
# 0. bindings
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_binding_i9n():
    Base.metadata.clear()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        async def flag(cls, ctx):
            ctx["flagged"] = True

    client, api, _, engine = create_client(Item)
    assert any(callable(h) for h in api.hooks.Item.create.PRE_HANDLER)
    await client.aclose()
    engine.dispose()


# ---------------------------------------------------------------------------
# 1. request and response schemas
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_request_response_schema_i9n():
    Base.metadata.clear()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="POST_RESPONSE")
        async def modify(cls, ctx):
            ctx["response"].result["hook"] = True

    client, _, _, engine = create_client(Item)
    res = await client.post("/item", json={"id": str(uuid4()), "name": "a"})
    assert res.status_code == 201
    assert res.json()["hook"] is True
    await client.aclose()
    engine.dispose()


# ---------------------------------------------------------------------------
# 2. columns
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_columns_i9n():
    Base.metadata.clear()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        async def collect_cols(cls, ctx):
            ctx["cols"] = list(cls.__table__.columns.keys())

        @hook_ctx(ops="create", phase="POST_RESPONSE")
        async def expose(cls, ctx):
            ctx["response"].result["cols"] = ctx["cols"]

    client, _, _, engine = create_client(Item)
    res = await client.post("/item", json={"id": str(uuid4()), "name": "x"})
    assert set(res.json()["cols"]) == {"id", "name"}
    await client.aclose()
    engine.dispose()


# ---------------------------------------------------------------------------
# 3. defaults and value resolution
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_defaults_resolution_i9n():
    Base.metadata.clear()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=True)

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        async def default_name(cls, ctx):
            ctx.setdefault("payload", {})
            ctx["payload"].setdefault("name", "default")

    client, _, _, engine = create_client(Item)
    res = await client.post("/item", json={"id": str(uuid4())})
    assert res.status_code == 201
    assert res.json()["name"] == "default"
    await client.aclose()
    engine.dispose()


# ---------------------------------------------------------------------------
# 4. internal orm models
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_internal_model_i9n():
    Base.metadata.clear()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        async def capture_model(cls, ctx):
            ctx["model_name"] = cls.__name__

        @hook_ctx(ops="create", phase="POST_RESPONSE")
        async def expose_model(cls, ctx):
            ctx["response"].result["model"] = ctx["model_name"]

    client, _, _, engine = create_client(Item)
    res = await client.post("/item", json={"id": str(uuid4()), "name": "a"})
    assert res.json()["model"] == "Item"
    await client.aclose()
    engine.dispose()


# ---------------------------------------------------------------------------
# 5. openapi.json
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_openapi_json_i9n():
    Base.metadata.clear()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        async def noop(cls, ctx):
            pass

    client, _, _, engine = create_client(Item)
    res = await client.get("/openapi.json")
    assert "/item" in res.json()["paths"]
    await client.aclose()
    engine.dispose()


# ---------------------------------------------------------------------------
# 6. storage & sqlalchemy
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_storage_sqlalchemy_i9n():
    Base.metadata.clear()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="POST_COMMIT")
        async def count_rows(cls, ctx):
            result = ctx["db"].execute(select(func.count()).select_from(cls)).scalar()
            ctx["count"] = result

        @hook_ctx(ops="create", phase="POST_RESPONSE")
        async def expose_count(cls, ctx):
            ctx["response"].result["count"] = ctx["count"]

    client, _, _, engine = create_client(Item)
    res = await client.post("/item", json={"id": str(uuid4()), "name": "a"})
    assert res.json()["count"] == 1
    await client.aclose()
    engine.dispose()


# ---------------------------------------------------------------------------
# 7. rest calls
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_rest_call_i9n():
    Base.metadata.clear()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="POST_RESPONSE")
        async def mark(cls, ctx):
            ctx["response"].result["phase"] = "rest"

    client, _, _, engine = create_client(Item)
    res = await client.post("/item", json={"id": str(uuid4()), "name": "a"})
    assert res.json()["phase"] == "rest"
    await client.aclose()
    engine.dispose()


# ---------------------------------------------------------------------------
# 8. rpc methods
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_rpc_method_i9n():
    Base.metadata.clear()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="POST_RESPONSE")
        async def mark(cls, ctx):
            ctx["response"].result["phase"] = "rpc"

    client, _, _, engine = create_client(Item)
    res = await client.post(
        "/rpc",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "Item.create",
            "params": {"name": "a"},
        },
    )
    assert res.json()["result"]["phase"] == "rpc"
    await client.aclose()
    engine.dispose()


# ---------------------------------------------------------------------------
# 9. core.crud
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_core_crud_i9n():
    Base.metadata.clear()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="POST_COMMIT")
        async def mark(cls, ctx):
            ctx["response"].result["via"] = "core"

    client, api, SessionLocal, engine = create_client(Item)
    with SessionLocal() as session:
        result = await api.core.Item.create(
            {"id": str(uuid4()), "name": "x"}, db=session
        )
    assert result["via"] == "core"
    await client.aclose()
    engine.dispose()


# ---------------------------------------------------------------------------
# 10. hookz
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_hookz_i9n():
    Base.metadata.clear()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="POST_COMMIT")
        async def marker(cls, ctx):
            pass

    client, _, _, engine = create_client(Item)
    res = await client.get("/system/hookz")
    data = res.json()
    assert "Item" in data and "create" in data["Item"]
    assert any("marker" in s for s in data["Item"]["create"]["POST_COMMIT"])
    await client.aclose()
    engine.dispose()


# ---------------------------------------------------------------------------
# 11. atomz
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_atomz_i9n():
    Base.metadata.clear()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        async def capture(cls, ctx):
            ctx["captured"] = ctx["payload"]["name"]

        @hook_ctx(ops="create", phase="POST_RESPONSE")
        async def expose(cls, ctx):
            ctx["response"].result["captured"] = ctx["captured"]

    client, _, _, engine = create_client(Item)
    res = await client.post("/item", json={"id": str(uuid4()), "name": "alpha"})
    assert res.json()["captured"] == "alpha"
    await client.aclose()
    engine.dispose()


# ---------------------------------------------------------------------------
# 12. system steps
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_system_steps_i9n():
    Base.metadata.clear()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="POST_COMMIT")
        async def marker(cls, ctx):
            pass

    client, _, _, engine = create_client(Item)
    res = await client.get("/system/planz")
    data = res.json()
    steps = data["Item"]["create"]
    assert "sys:handler:crud@HANDLER" in steps
    await client.aclose()
    engine.dispose()
