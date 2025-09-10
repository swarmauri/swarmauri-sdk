import pytest
from tigrbl.types import App
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select

from tigrbl import TigrblApp
from tigrbl.types import Column, String
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.hook import hook_ctx


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def create_client(model_cls):
    """Build a FastAPI app with Tigrbl v3 and return an AsyncClient."""
    app = App()
    api = TigrblApp(engine={"kind": "sqlite", "memory": True})
    api.include_model(model_cls)
    api.mount_jsonrpc()
    api.attach_diagnostics()

    from tigrbl.engine import resolver as _resolver

    prov = _resolver.resolve_provider(api=api)
    engine, SessionLocal = prov.ensure()
    Base.metadata.create_all(engine)

    app.include_router(api.router)
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    return client, api, SessionLocal


# ---------------------------------------------------------------------------
# 0. bindings
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_binding_i9n():
    Base.metadata.clear()
    Base.registry.dispose()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        async def flag(cls, ctx):
            ctx["flagged"] = True

    client, api, _ = create_client(Item)
    assert any(callable(h) for h in api.hooks.Item.create.PRE_HANDLER)
    await client.aclose()


# ---------------------------------------------------------------------------
# 1. request and response schemas
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_request_response_schema_i9n():
    Base.metadata.clear()
    Base.registry.dispose()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="POST_RESPONSE")
        async def modify(cls, ctx):
            ctx["response"].result["hook"] = True

    client, _, _ = create_client(Item)
    res = await client.post("/item", json={"name": "a"})
    assert res.status_code == 201
    assert res.json()["hook"] is True
    await client.aclose()


# ---------------------------------------------------------------------------
# 2. columns
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_columns_i9n():
    Base.metadata.clear()
    Base.registry.dispose()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        async def collect_cols(cls, ctx):
            ctx["cols"] = list(cls.__table__.columns.keys())

        @hook_ctx(ops="create", phase="POST_RESPONSE")
        async def expose(cls, ctx):
            ctx["response"].result["cols"] = ctx["cols"]

    client, _, _ = create_client(Item)
    res = await client.post("/item", json={"name": "x"})
    assert set(res.json()["cols"]) == {"id", "name"}
    await client.aclose()


# ---------------------------------------------------------------------------
# 3. defaults and value resolution
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_defaults_resolution_i9n():
    Base.metadata.clear()
    Base.registry.dispose()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=True)

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        async def default_name(cls, ctx):
            ctx.setdefault("payload", {})
            ctx["payload"].setdefault("name", "default")

    client, _, _ = create_client(Item)
    res = await client.post("/item", json={})
    assert res.status_code == 201
    assert res.json()["name"] == "default"
    await client.aclose()


# ---------------------------------------------------------------------------
# 4. internal orm models
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_internal_model_i9n():
    Base.metadata.clear()
    Base.registry.dispose()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        async def capture_model(cls, ctx):
            ctx["model_name"] = cls.__name__

        @hook_ctx(ops="create", phase="POST_RESPONSE")
        async def expose_model(cls, ctx):
            ctx["response"].result["model"] = ctx["model_name"]

    client, _, _ = create_client(Item)
    res = await client.post("/item", json={"name": "a"})
    assert res.json()["model"] == "Item"
    await client.aclose()


# ---------------------------------------------------------------------------
# 5. openapi.json
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_openapi_json_i9n():
    Base.metadata.clear()
    Base.registry.dispose()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        async def noop(cls, ctx):
            pass

    client, _, _ = create_client(Item)
    res = await client.get("/openapi.json")
    assert "/item" in res.json()["paths"]
    await client.aclose()


# ---------------------------------------------------------------------------
# 6. storage & sqlalchemy
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_storage_sqlalchemy_i9n():
    Base.metadata.clear()
    Base.registry.dispose()

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

    client, _, _ = create_client(Item)
    res = await client.post("/item", json={"name": "a"})
    assert res.json()["count"] == 1
    await client.aclose()


# ---------------------------------------------------------------------------
# 7. rest calls
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_rest_call_i9n():
    Base.metadata.clear()
    Base.registry.dispose()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="POST_RESPONSE")
        async def mark(cls, ctx):
            ctx["response"].result["phase"] = "rest"

    client, _, _ = create_client(Item)
    res = await client.post("/item", json={"name": "a"})
    assert res.json()["phase"] == "rest"
    await client.aclose()


# ---------------------------------------------------------------------------
# 8. rpc methods
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_rpc_method_i9n():
    Base.metadata.clear()
    Base.registry.dispose()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="POST_RESPONSE")
        async def mark(cls, ctx):
            ctx["response"].result["phase"] = "rpc"

    client, _, _ = create_client(Item)
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


# ---------------------------------------------------------------------------
# 9. core.crud
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_core_crud_i9n():
    Base.metadata.clear()
    Base.registry.dispose()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="POST_COMMIT")
        async def mark(cls, ctx):
            ctx["response"].result["via"] = "core"

    client, api, SessionLocal = create_client(Item)
    with SessionLocal() as session:
        result = await api.core.Item.create({"name": "x"}, db=session)
    assert result["via"] == "core"
    await client.aclose()


# ---------------------------------------------------------------------------
# 10. hookz
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_hookz_i9n():
    Base.metadata.clear()
    Base.registry.dispose()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="POST_COMMIT")
        async def marker(cls, ctx):
            pass

    client, _, _ = create_client(Item)
    res = await client.get("/system/hookz")
    data = res.json()
    assert "Item" in data and "create" in data["Item"]
    assert any("marker" in s for s in data["Item"]["create"]["POST_COMMIT"])
    await client.aclose()


# ---------------------------------------------------------------------------
# 11. atomz
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_atomz_i9n():
    Base.metadata.clear()
    Base.registry.dispose()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        async def capture(cls, ctx):
            ctx["captured"] = ctx["payload"]["name"]

        @hook_ctx(ops="create", phase="POST_RESPONSE")
        async def expose(cls, ctx):
            ctx["response"].result["captured"] = ctx["captured"]

    client, _, _ = create_client(Item)
    res = await client.post("/item", json={"name": "alpha"})
    assert res.json()["captured"] == "alpha"
    await client.aclose()


# ---------------------------------------------------------------------------
# 12. system steps
# ---------------------------------------------------------------------------


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_ctx_system_steps_i9n():
    Base.metadata.clear()
    Base.registry.dispose()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="POST_COMMIT")
        async def marker(cls, ctx):
            pass

    client, _, _ = create_client(Item)
    res = await client.get("/system/kernelz")
    data = res.json()
    steps = data["Item"]["create"]
    assert "HANDLER:hook:wire:tigrbl:core:crud:ops:create@HANDLER" in steps
    await client.aclose()
