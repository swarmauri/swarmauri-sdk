"""Lesson 10.4: Calling JSON-RPC operations from a client."""

import httpx
import inspect
import pytest
from tigrbl_client import TigrblClient

from examples._support import pick_unused_port, run_uvicorn_app, stop_server
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import App as FastAPI
from tigrbl.types import Column, String


@pytest.mark.asyncio
async def test_rpc_call_works_over_jsonrpc():
    """Confirm RPC calls succeed against the JSON-RPC mount.

    Purpose: show that TigrblClient can invoke registered operations remotely.
    Design practice: use the explicit model-prefixed method name.
    """

    # Setup: define a model to expose over JSON-RPC.
    class LessonRPCClient(Base, GUIDPk):
        __tablename__ = "lesson_rpc_client"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Deployment: build the API, mount JSON-RPC, and attach diagnostics.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(LessonRPCClient)
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    api.mount_jsonrpc(prefix="/rpc")

    app = FastAPI()
    app.include_router(api.router)
    api.attach_diagnostics(prefix="", app=app)

    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)

    # Test: invoke the list method over JSON-RPC.
    client = TigrblClient(handle.base_url + "/rpc")
    result = await client.acall(f"{LessonRPCClient.__name__}.list", params={})

    # Assertion: the call returns a list payload.
    assert isinstance(result, list)
    await client.aclose()
    await stop_server(handle)


@pytest.mark.asyncio
async def test_rpc_list_reflects_rest_creates():
    """Show RPC reads reflect REST writes for parity.

    Purpose: verify that creating via REST is visible through JSON-RPC list.
    Design practice: keep RPC/REST parity to reduce client confusion.
    """

    # Setup: define a model for REST/RPC parity checks.
    class LessonRPCClientList(Base, GUIDPk):
        __tablename__ = "lesson_rpc_client_list"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Deployment: initialize app, mount JSON-RPC, and attach diagnostics.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(LessonRPCClientList)
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    api.mount_jsonrpc(prefix="/rpc")

    app = FastAPI()
    app.include_router(api.router)
    api.attach_diagnostics(prefix="", app=app)

    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)

    # Test: create a record via REST so RPC can read it back.
    async with httpx.AsyncClient(base_url=handle.base_url, timeout=10.0) as client:
        response = await client.post(
            f"/{LessonRPCClientList.__name__.lower()}",
            json={"name": "delta"},
        )

        # Assertion: REST create succeeds.
        assert response.status_code in {200, 201}

    # Test: list via JSON-RPC.
    client = TigrblClient(handle.base_url + "/rpc")
    result = await client.acall(f"{LessonRPCClientList.__name__}.list", params={})

    # Assertion: the RPC list contains the REST-created record.
    assert any(item["name"] == "delta" for item in result)
    await client.aclose()
    await stop_server(handle)
