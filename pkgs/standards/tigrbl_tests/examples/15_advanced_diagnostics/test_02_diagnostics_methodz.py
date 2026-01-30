import httpx
import pytest
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String

from examples._support import pick_unused_port, run_uvicorn_app, stop_server


@pytest.mark.asyncio
async def test_diagnostics_methodz_lists_operations():
    """Teach using the ``/methodz`` endpoint to list available operations.

    Purpose:
        Verify that method discovery returns model operations so clients and
        tooling can enumerate callable methods.

    What this shows:
        - Diagnostics endpoints reveal registered RPC methods.
        - The list includes default operations like ``list``.

    Best practice:
        Expose method inventories in non-production environments for rapid
        debugging and client generation.
    """

    # Setup: define a model to populate default operations.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_methodz_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    # Deployment: create the app and attach diagnostics.
    app = TigrblApp(engine=mem(async_=False), system_prefix="")
    app.include_model(Widget)
    app.initialize()
    app.attach_diagnostics()

    # Deployment: run the app under Uvicorn.
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    # Test: fetch the method listing.
    async with httpx.AsyncClient(base_url=handle.base_url, timeout=10.0) as client:
        response = await client.get("/methodz")
        assert response.status_code == 200
        methods = {entry["method"] for entry in response.json()["methods"]}
        # Assertion: the default list operation is present.
        assert f"{Widget.__name__}.list" in methods
    await stop_server(handle)


@pytest.mark.asyncio
async def test_methodz_payload_has_expected_shape():
    """Reinforce the structure of the method listing response.

    Purpose:
        Confirm that ``/methodz`` returns a JSON object with a ``methods`` list
        containing objects with a ``method`` key.

    What this shows:
        - The diagnostics response is structured and machine-readable.
        - Entries use a stable shape for tooling consumption.

    Best practice:
        Validate response shapes for diagnostics endpoints to keep them
        reliable for automated tooling.
    """

    # Setup: define a model for response shape validation.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_methodz_shape_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    # Deployment: create the app and attach diagnostics.
    app = TigrblApp(engine=mem(async_=False), system_prefix="")
    app.include_model(Widget)
    app.initialize()
    app.attach_diagnostics()

    # Deployment: run the app under Uvicorn.
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    # Test: inspect the method listing payload shape.
    async with httpx.AsyncClient(base_url=handle.base_url, timeout=10.0) as client:
        response = await client.get("/methodz")
        assert response.status_code == 200
        payload = response.json()
        # Assertion: the response includes a non-empty methods list.
        assert isinstance(payload.get("methods"), list)
        assert payload["methods"]
        assert "method" in payload["methods"][0]
    await stop_server(handle)
