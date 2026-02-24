"""Integration coverage for engine precedence, interning, and uvicorn routing.

These scenarios validate resolver binding across TigrblApp/TigrblRouter surfaces,
including REST + JSON-RPC flows against a live uvicorn server.
"""

from __future__ import annotations

import httpx
import pytest
from sqlalchemy import Column, String

from tigrbl import Base, TigrblRouter, TigrblApp, engine_ctx, op_ctx
from tigrbl.engine import resolver
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk

from .uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrblapp_multi_table_engine_precedence_uvicorn() -> None:
    """Verify app defaults, table overrides, and REST/RPC routing with uvicorn.

    Steps:
        1) Build an app with two tables and distinct engine configs.
        2) Assert resolver precedence and provider interning.
        3) Start uvicorn and exercise REST + JSON-RPC calls.
    """
    # Step 1: Define models and engine configs for the app + tables.
    app_engine = {**mem(async_=False), "tag": "app-default"}
    table_engine = {**mem(async_=False), "tag": "table-override"}

    class AppWidget(Base, GUIDPk):
        __tablename__ = "app_widgets"
        __resource__ = "app-widget"
        name = Column(String, nullable=False)

    @engine_ctx(table_engine)
    class AppGadget(Base, GUIDPk):
        __tablename__ = "app_gadgets"
        __resource__ = "app-gadget"
        name = Column(String, nullable=False)

    app = TigrblApp(engine=app_engine)
    app.include_models([AppWidget, AppGadget])
    app.install_engines(models=tuple(app.models.values()))
    app.mount_jsonrpc()
    app.initialize()

    # Step 2: Assert resolver precedence + interning behavior.
    default_provider = resolver.resolve_provider()
    widget_provider = resolver.resolve_provider(model=AppWidget)
    gadget_provider = resolver.resolve_provider(model=AppGadget)
    assert widget_provider is default_provider
    assert gadget_provider is not default_provider
    assert app.engine == app_engine
    assert AppGadget.table_config["engine"] == table_engine

    # Step 3: Start uvicorn and validate REST + JSON-RPC calls.
    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        async with httpx.AsyncClient() as client:
            rest_widget = await client.post(
                f"{base_url}/app-widget", json={"name": "alpha"}
            )
            rest_gadget = await client.post(
                f"{base_url}/app-gadget", json={"name": "beta"}
            )
            rpc_payload = {
                "jsonrpc": "2.0",
                "method": "AppWidget.create",
                "params": {"name": "rpc-widget"},
                "id": 1,
            }
            rpc_response = await client.post(f"{base_url}/rpc/", json=rpc_payload)

        assert rest_widget.status_code == 201
        assert rest_gadget.status_code == 201
        assert rpc_response.status_code == 200
        assert rpc_response.json()["result"]["name"] == "rpc-widget"
    finally:
        await stop_uvicorn_server(server, task)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrblapi_multi_table_engine_binding_uvicorn() -> None:
    """Validate API-level engine defaults and table overrides via uvicorn.

    Steps:
        1) Build a TigrblRouter with two tables and a table override.
        2) Assert resolver bindings for router + models.
        3) Exercise REST + JSON-RPC routes in uvicorn.
    """
    # Step 1: Define models and engine configs for the API.
    api_engine = {**mem(async_=False), "tag": "router-default"}
    table_engine = {**mem(async_=False), "tag": "router-table"}

    class ApiWidget(Base, GUIDPk):
        __tablename__ = "api_widgets"
        __resource__ = "router-widget"
        name = Column(String, nullable=False)

    @engine_ctx(table_engine)
    class ApiGadget(Base, GUIDPk):
        __tablename__ = "api_gadgets"
        __resource__ = "router-gadget"
        name = Column(String, nullable=False)

    router = TigrblRouter(engine=api_engine)
    router.include_models([ApiWidget, ApiGadget])
    router.install_engines(models=tuple(router.models.values()))
    router.mount_jsonrpc()
    router.initialize()

    app = TigrblApp()
    app.include_router(router.router, prefix="/router")

    # Step 2: Assert resolver bindings (router vs table overrides).
    api_provider = resolver.resolve_provider(router=router)
    widget_provider = resolver.resolve_provider(router=router, model=ApiWidget)
    gadget_provider = resolver.resolve_provider(router=router, model=ApiGadget)
    assert api_provider is widget_provider
    assert gadget_provider is not api_provider
    assert router.engine == api_engine
    assert ApiGadget.table_config["engine"] == table_engine

    # Step 3: Start uvicorn and validate REST + JSON-RPC calls.
    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        async with httpx.AsyncClient() as client:
            rest_widget = await client.post(
                f"{base_url}/router/router-widget", json={"name": "widget"}
            )
            rest_gadget = await client.post(
                f"{base_url}/router/router-gadget", json={"name": "gadget"}
            )
            rpc_payload = {
                "jsonrpc": "2.0",
                "method": "ApiWidget.create",
                "params": {"name": "rpc-widget"},
                "id": 1,
            }
            rpc_response = await client.post(
                f"{base_url}/router/rpc/", json=rpc_payload
            )

        assert rest_widget.status_code == 201
        assert rest_gadget.status_code == 201
        assert rpc_response.status_code == 200
        assert rpc_response.json()["result"]["name"] == "rpc-widget"
    finally:
        await stop_uvicorn_server(server, task)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_multi_api_precedence_dedupe_and_op_engine_uvicorn() -> None:
    """Cover multi-API precedence, dedupe, and op-level engine overrides.

    Steps:
        1) Build two APIs with multiple tables and distinct engine configs.
        2) Attach an op with a unique engine to one table.
        3) Assert resolver precedence + interning, then validate REST/RPC calls.
    """
    # Step 1: Define engine configs and models.
    app_engine = {**mem(async_=False), "tag": "app-shared"}
    api_one_engine = {**mem(async_=False), "tag": "app-shared"}
    api_two_engine = {**mem(async_=False), "tag": "router-two"}
    model_engine = {**mem(async_=False), "tag": "model-two"}
    op_engine = {**mem(async_=False), "tag": "op-override"}

    class AlphaWidget(Base, GUIDPk):
        __tablename__ = "alpha_widgets"
        __resource__ = "alpha-widget"
        name = Column(String, nullable=False)

    class AlphaGadget(Base, GUIDPk):
        __tablename__ = "alpha_gadgets"
        __resource__ = "alpha-gadget"
        name = Column(String, nullable=False)

    @engine_ctx(model_engine)
    class BetaWidget(Base, GUIDPk):
        __tablename__ = "beta_widgets"
        __resource__ = "beta-widget"
        name = Column(String, nullable=False)

        @engine_ctx(op_engine)
        @op_ctx(alias="ping", arity="collection")
        async def ping(cls, ctx):
            return {"status": "ok", "engine": "op"}

    class BetaGadget(Base, GUIDPk):
        __tablename__ = "beta_gadgets"
        __resource__ = "beta-gadget"
        name = Column(String, nullable=False)

    api_one = TigrblRouter(engine=api_one_engine)
    api_one.include_models([AlphaWidget, AlphaGadget])
    api_one.initialize()
    api_one.install_engines(models=tuple(api_one.models.values()))
    api_one.mount_jsonrpc()

    api_two = TigrblRouter(engine=api_two_engine)
    api_two.include_models([BetaWidget, BetaGadget])
    api_two.initialize()
    api_two.install_engines(models=tuple(api_two.models.values()))
    api_two.mount_jsonrpc()
    # Step 1a: Explicitly register the op override to mirror resolver precedence.
    resolver.register_op(BetaWidget, "ping", op_engine)

    app = TigrblApp(engine=app_engine, apis=[api_one, api_two])
    app.include_router(api_one.router, prefix="/alpha")
    app.include_router(api_two.router, prefix="/beta")
    app.install_engines(models=tuple(app.models.values()))
    app.initialize()

    # Step 2: Assert resolver precedence and dedupe across app/router/model/op.
    default_provider = resolver.resolve_provider()
    api_one_provider = resolver.resolve_provider(router=api_one)
    api_two_provider = resolver.resolve_provider(router=api_two)
    beta_model_provider = resolver.resolve_provider(router=api_two, model=BetaWidget)
    beta_op_provider = resolver.resolve_provider(
        router=api_two, model=BetaWidget, op_alias="ping"
    )

    assert default_provider is api_one_provider
    assert api_two_provider is not default_provider
    assert beta_model_provider is not api_two_provider
    assert beta_op_provider is not beta_model_provider
    assert beta_op_provider is not api_two_provider
    assert api_one.engine == api_one_engine
    assert api_two.engine == api_two_engine
    assert BetaWidget.table_config["engine"] == model_engine

    # Step 3: Validate REST + JSON-RPC routing through uvicorn.
    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        async with httpx.AsyncClient() as client:
            rest_alpha = await client.post(
                f"{base_url}/alpha/alpha-widget", json={"name": "alpha"}
            )
            rest_beta = await client.post(
                f"{base_url}/beta/beta-widget", json={"name": "beta"}
            )
            rpc_payload = {
                "jsonrpc": "2.0",
                "method": "BetaWidget.ping",
                "params": {},
                "id": 42,
            }
            rpc_response = await client.post(f"{base_url}/beta/rpc/", json=rpc_payload)

        assert rest_alpha.status_code == 201
        assert rest_beta.status_code == 201
        assert rpc_response.status_code == 200
        assert rpc_response.json()["result"]["status"] == "ok"
    finally:
        await stop_uvicorn_server(server, task)
