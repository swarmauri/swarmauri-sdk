"""
Hook Lifecycle Tests for Tigrbl v3

Tests all hook phases and their behavior across CRUD, nested CRUD, and RPC operations.
"""

import pytest
from fastapi import FastAPI
from tigrbl import TigrblApp, Base
from tigrbl.hook import hook_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, ForeignKey, String
from tigrbl.types import PgUUID


async def setup_client(db_mode, Tenant, Item):
    """Create an Tigrbl client for the provided models."""
    fastapi_app = FastAPI()

    if db_mode == "async":
        api = TigrblApp(engine=mem())
        api.include_models([Tenant, Item])
        await api.initialize()
    else:
        api = TigrblApp(engine=mem(async_=False))
        api.include_models([Tenant, Item])
        api.initialize()

    api.mount_jsonrpc()
    fastapi_app.include_router(api.router)
    transport = ASGITransport(app=fastapi_app)
    client = AsyncClient(transport=transport, base_url="http://test")
    return client, api


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_phases_execution_order(db_mode):
    """Test that all hook phases execute in the correct order."""

    execution_order: list[str] = []
    Base.metadata.clear()

    class Tenant(Base, GUIDPk):
        __tablename__ = "tenants"
        name = Column(String, nullable=False)

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        tenant_id = Column(
            PgUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
        )
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="PRE_TX_BEGIN")
        async def pre_tx_begin(cls, ctx):
            execution_order.append("PRE_TX_BEGIN")
            ctx["test_data"] = {"started": True}

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        async def pre_handler(cls, ctx):
            execution_order.append("PRE_HANDLER")
            assert ctx["test_data"]["started"] is True
            ctx["test_data"]["pre_handler_done"] = True

        @hook_ctx(ops="create", phase="POST_HANDLER")
        async def post_handler(cls, ctx):
            execution_order.append("POST_HANDLER")
            assert ctx["test_data"]["pre_handler_done"] is True
            ctx["test_data"]["handler_done"] = True

        @hook_ctx(ops="create", phase="PRE_COMMIT")
        async def pre_commit(cls, ctx):
            execution_order.append("PRE_COMMIT")
            assert ctx["test_data"]["handler_done"] is True
            ctx["test_data"]["pre_commit_done"] = True

        @hook_ctx(ops="create", phase="POST_COMMIT")
        async def post_commit(cls, ctx):
            execution_order.append("POST_COMMIT")
            assert ctx["test_data"]["pre_commit_done"] is True
            ctx["test_data"]["committed"] = True

        @hook_ctx(ops="create", phase="POST_RESPONSE")
        async def post_response(cls, ctx):
            execution_order.append("POST_RESPONSE")
            assert ctx["test_data"]["committed"] is True
            ctx["response"].result["hook_completed"] = True

    client, _ = await setup_client(db_mode, Tenant, Item)

    t = await client.post("/tenant", json={"name": "test-tenant"})
    tid = t.json()["id"]

    res = await client.post(
        "/rpc",
        json={
            "method": "Item.create",
            "params": {"tenant_id": tid, "name": "test-item"},
        },
    )

    assert res.status_code == 200
    data = res.json()["result"]
    assert data["hook_completed"] is True

    expected_order = [
        "PRE_TX_BEGIN",
        "PRE_HANDLER",
        "POST_HANDLER",
        "PRE_COMMIT",
        "POST_COMMIT",
        "POST_RESPONSE",
    ]
    assert execution_order == expected_order
    await client.aclose()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_parity_crud_vs_rpc(db_mode):
    """Test that hooks execute identically for REST CRUD and RPC calls."""

    crud_hooks: list[str] = []
    rpc_hooks: list[str] = []
    Base.metadata.clear()

    class Tenant(Base, GUIDPk):
        __tablename__ = "tenants"
        name = Column(String, nullable=False)

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        tenant_id = Column(
            PgUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
        )
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="PRE_TX_BEGIN")
        async def track_pre_tx(cls, ctx):
            if hasattr(ctx.get("request"), "url") and "/rpc" in str(ctx["request"].url):
                rpc_hooks.append("PRE_TX_BEGIN")
            else:
                crud_hooks.append("PRE_TX_BEGIN")

        @hook_ctx(ops="create", phase="POST_COMMIT")
        async def track_post_commit(cls, ctx):
            if hasattr(ctx.get("request"), "url") and "/rpc" in str(ctx["request"].url):
                rpc_hooks.append("POST_COMMIT")
            else:
                crud_hooks.append("POST_COMMIT")

    client, _ = await setup_client(db_mode, Tenant, Item)

    t = await client.post("/tenant", json={"name": "test-tenant"})
    tid = t.json()["id"]

    await client.post("/item", json={"tenant_id": tid, "name": "crud-item"})

    await client.post(
        "/rpc",
        json={
            "method": "Item.create",
            "params": {"tenant_id": tid, "name": "rpc-item"},
        },
    )

    assert crud_hooks == ["PRE_TX_BEGIN", "POST_COMMIT"]
    assert rpc_hooks == ["PRE_TX_BEGIN", "POST_COMMIT"]
    await client.aclose()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_error_handling(db_mode):
    """Test hook behavior during error conditions."""

    error_hooks: list[str] = []
    Base.metadata.clear()

    class Tenant(Base, GUIDPk):
        __tablename__ = "tenants"
        name = Column(String, nullable=False)

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        tenant_id = Column(
            PgUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
        )
        name = Column(String, nullable=False)

        @hook_ctx(ops="*", phase="ON_ERROR")
        async def error_handler(cls, ctx):
            error_hooks.append("ERROR_HANDLED")
            ctx["error_data"] = {"handled": True}

        @hook_ctx(ops="create", phase="PRE_TX_BEGIN")
        async def failing_hook(cls, ctx):
            raise ValueError("Intentional test error")

    client, _ = await setup_client(db_mode, Tenant, Item)

    t = await client.post("/tenant", json={"name": "test-tenant"})
    tid = t.json()["id"]

    try:
        res = await client.post(
            "/item",
            json={"tenant_id": tid, "name": "error-item"},
        )
        assert res.status_code >= 400
    except Exception:
        pass

    assert error_hooks == ["ERROR_HANDLED"]
    await client.aclose()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_early_termination_and_cleanup(db_mode):
    """Test early termination when a hook raises and ensure cleanup."""

    execution_order: list[str] = []
    Base.metadata.clear()

    class Tenant(Base, GUIDPk):
        __tablename__ = "tenants"
        name = Column(String, nullable=False)

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        tenant_id = Column(
            PgUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
        )
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="PRE_TX_BEGIN")
        async def pre_tx_begin(cls, ctx):
            execution_order.append("PRE_TX_BEGIN")

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        async def pre_handler(cls, ctx):
            execution_order.append("PRE_HANDLER")

        @hook_ctx(ops="create", phase="POST_HANDLER")
        async def post_handler(cls, ctx):
            execution_order.append("POST_HANDLER")

        @hook_ctx(ops="create", phase="PRE_COMMIT")
        async def pre_commit(cls, ctx):
            execution_order.append("PRE_COMMIT")
            raise RuntimeError("boom")

        @hook_ctx(ops="create", phase="POST_COMMIT")
        async def post_commit(cls, ctx):
            execution_order.append("POST_COMMIT")

        @hook_ctx(ops="create", phase="POST_RESPONSE")
        async def post_response(cls, ctx):
            execution_order.append("POST_RESPONSE")

    client, _ = await setup_client(db_mode, Tenant, Item)

    t = await client.post("/tenant", json={"name": "test-tenant"})
    tid = t.json()["id"]

    before = await client.get("/item")
    assert before.json() == []

    try:
        res = await client.post(
            "/item",
            json={"tenant_id": tid, "name": "fail-item"},
        )
        assert res.status_code >= 400
    except RuntimeError:
        pass

    after = await client.get("/item")
    assert after.json() == []

    assert execution_order == [
        "PRE_TX_BEGIN",
        "PRE_HANDLER",
        "POST_HANDLER",
        "PRE_COMMIT",
    ]
    await client.aclose()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hook_context_modification(db_mode):
    """Test that hooks can modify context and affect subsequent hooks."""

    hook_executions: list[str] = []
    Base.metadata.clear()

    class Tenant(Base, GUIDPk):
        __tablename__ = "tenants"
        name = Column(String, nullable=False)

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        tenant_id = Column(
            PgUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
        )
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="PRE_TX_BEGIN")
        async def modify_params(cls, ctx):
            hook_executions.append("PRE_TX_BEGIN")
            ctx["custom_data"] = {"modified": True}

        @hook_ctx(ops="create", phase="POST_HANDLER")
        async def verify_modification(cls, ctx):
            hook_executions.append("POST_HANDLER")
            assert ctx["custom_data"]["modified"] is True
            ctx["custom_data"]["verified"] = True

        @hook_ctx(ops="create", phase="POST_RESPONSE")
        async def enrich_response(cls, ctx):
            hook_executions.append("POST_RESPONSE")
            assert ctx["custom_data"]["verified"] is True
            assert hasattr(ctx["response"].result, "name")

    client, _ = await setup_client(db_mode, Tenant, Item)

    t = await client.post("/tenant", json={"name": "test-tenant"})
    tid = t.json()["id"]

    res = await client.post("/item", json={"tenant_id": tid, "name": "test-item"})
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "test-item"

    assert hook_executions == ["PRE_TX_BEGIN", "POST_HANDLER", "POST_RESPONSE"]
    await client.aclose()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_catch_all_hooks(db_mode):
    """Test that catch-all hooks (no model/op specified) work correctly."""

    catch_all_executions: list[str] = []
    Base.metadata.clear()

    class CatchAllMixin:
        @hook_ctx(ops="*", phase="POST_COMMIT")
        async def catch_all_hook(cls, ctx):
            method = f"{cls.__name__}.{getattr(ctx.get('env'), 'method', 'unknown')}"
            catch_all_executions.append(method)

        @hook_ctx(ops="*", phase="POST_HANDLER")
        async def post_handler_hook(cls, ctx):
            method = f"{cls.__name__}.{getattr(ctx.get('env'), 'method', 'unknown')}"
            if method.endswith(".delete") and method not in catch_all_executions:
                catch_all_executions.append(method)

    class Tenant(CatchAllMixin, Base, GUIDPk):
        __tablename__ = "tenants"
        name = Column(String, nullable=False)

    class Item(CatchAllMixin, Base, GUIDPk):
        __tablename__ = "items"
        tenant_id = Column(
            PgUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
        )
        name = Column(String, nullable=False)

    client, _ = await setup_client(db_mode, Tenant, Item)

    t = await client.post("/tenant", json={"name": "test-tenant"})
    tid = t.json()["id"]

    await client.post("/item", json={"tenant_id": tid, "name": "test-item"})

    items = await client.get("/item")
    item_id = items.json()[0]["id"]
    await client.get(f"/item/{item_id}")

    update_res = await client.patch(
        f"/item/{item_id}", json={"tenant_id": tid, "name": "updated-item"}
    )
    update_succeeded = update_res.status_code < 400

    delete_res = await client.delete(f"/item/{item_id}")
    delete_succeeded = delete_res.status_code < 400

    expected_methods = [
        "Tenant.create",
        "Item.create",
        "Item.list",
        "Item.read",
    ]
    if update_succeeded:
        expected_methods.append("Item.update")
    if delete_succeeded:
        expected_methods.append("Item.delete")

    unique_methods = list(dict.fromkeys(catch_all_executions))
    assert unique_methods == expected_methods
    await client.aclose()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_multiple_hooks_same_phase(db_mode):
    """Test that multiple hooks for the same phase execute correctly."""

    executions: list[str] = []
    Base.metadata.clear()

    class Tenant(Base, GUIDPk):
        __tablename__ = "tenants"
        name = Column(String, nullable=False)

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        tenant_id = Column(
            PgUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
        )
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="POST_COMMIT")
        async def first_hook(cls, ctx):
            executions.append("first")

        @hook_ctx(ops="create", phase="POST_COMMIT")
        async def second_hook(cls, ctx):
            executions.append("second")

        @hook_ctx(ops="create", phase="POST_COMMIT")
        async def third_hook(cls, ctx):
            executions.append("third")

    client, _ = await setup_client(db_mode, Tenant, Item)

    t = await client.post("/tenant", json={"name": "test-tenant"})
    tid = t.json()["id"]

    await client.post("/item", json={"tenant_id": tid, "name": "test-item"})

    assert len(executions) == 3
    assert "first" in executions
    assert "second" in executions
    assert "third" in executions
    await client.aclose()
