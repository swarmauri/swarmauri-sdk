import httpx
import pytest
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String
from tigrbl_client import TigrblClient

from examples._support import pick_unused_port, run_uvicorn_app, stop_server


@pytest.mark.asyncio
async def test_rpc_and_rest_parity_with_uvicorn():
    """Teach parity between REST and RPC in a live Uvicorn app.

    Purpose:
        Ensure a REST-created record is visible via the RPC list operation,
        proving consistent data paths across transports.

    What this shows:
        - REST and RPC share the same backend operations.
        - The JSON-RPC list endpoint sees REST-created data.

    Best practice:
        Validate parity between transports to prevent drift between REST and
        RPC behaviors.
    """

    # Setup: declare a model to exercise REST/RPC parity.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_parity_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    # Deployment: create the API with JSON-RPC and diagnostics enabled.
    app = TigrblApp(engine=mem(async_=False), system_prefix="")
    app.include_model(Widget)
    app.initialize()
    app.mount_jsonrpc(prefix="/rpc")
    app.attach_diagnostics()

    # Deployment: run the app under Uvicorn.
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    # Test: create a record via REST.
    async with httpx.AsyncClient(base_url=handle.base_url, timeout=10.0) as client:
        response = await client.post(
            f"/{Widget.__name__.lower()}",
            json={"name": "gamma"},
        )
        # Assertion: REST create responds successfully.
        assert response.status_code in {200, 201}

    # Test: list records via RPC and compare to REST-created data.
    rpc_client = TigrblClient(handle.base_url + "/rpc")
    rpc_response = await rpc_client.acall(f"{Widget.__name__}.list", params={})
    items = (
        rpc_response.get("items") if isinstance(rpc_response, dict) else rpc_response
    )
    # Assertion: RPC sees the REST-created item.
    assert items
    assert items[0]["name"] == "gamma"
    await rpc_client.aclose()
    await stop_server(handle)


@pytest.mark.asyncio
async def test_rest_list_includes_rest_created_item():
    """Reinforce that REST reads can see REST writes.

    Purpose:
        Confirm that a REST-created record appears in the REST list endpoint,
        demonstrating an end-to-end REST workflow.

    What this shows:
        - Default REST list operations are wired correctly.
        - Data persists across multiple REST calls.

    Best practice:
        Test both create and list flows to validate CRUD consistency.
    """

    # Setup: declare a model for REST-only parity validation.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_parity_rest_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    # Deployment: create the API and attach diagnostics for readiness.
    app = TigrblApp(engine=mem(async_=False), system_prefix="")
    app.include_model(Widget)
    app.initialize()
    app.attach_diagnostics()

    # Deployment: run the app under Uvicorn.
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    # Test: create a record via REST, then list it via REST.
    async with httpx.AsyncClient(base_url=handle.base_url, timeout=10.0) as client:
        create_response = await client.post(
            f"/{Widget.__name__.lower()}",
            json={"name": "delta"},
        )
        # Assertion: REST create returns success.
        assert create_response.status_code in {200, 201}

        list_response = await client.get(f"/{Widget.__name__.lower()}")
        assert list_response.status_code == 200
        items = list_response.json()
        # Assertion: the created item is visible in the list.
        assert items
        assert items[0]["name"] == "delta"
    await stop_server(handle)
