import httpx
import pytest
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String

from examples._support import pick_unused_port, run_uvicorn_app, stop_server


@pytest.mark.asyncio
async def test_kernelz_returns_operation_plan():
    """Teach how kernel diagnostics expose operation plans.

    Purpose:
        Ensure the kernel diagnostics endpoint returns a payload keyed by
        model name, indicating registered operations.

    What this shows:
        - Kernel diagnostics expose model-specific metadata.
        - The endpoint is ready once the server is running.

    Best practice:
        Use kernel diagnostics to verify which models and operations are wired
        before running integration tests.
    """

    # Setup: declare a model to populate kernel diagnostics.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_kernelz_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    # Deployment: create the app, include the model, and attach diagnostics.
    app = TigrblApp(engine=mem(async_=False), system_prefix="")
    app.include_model(Widget)
    app.initialize()
    app.attach_diagnostics()

    # Deployment: run the app under Uvicorn.
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    # Test: request the kernel diagnostics endpoint.
    async with httpx.AsyncClient(base_url=handle.base_url, timeout=10.0) as client:
        response = await client.get("/kernelz")
        assert response.status_code == 200
        payload = response.json()
        # Assertion: the model appears in the kernel payload.
        assert Widget.__name__ in payload
    await stop_server(handle)


@pytest.mark.asyncio
async def test_kernelz_payload_is_json_object():
    """Reinforce that kernel diagnostics return structured JSON.

    Purpose:
        Confirm that the kernel diagnostics endpoint responds with a JSON
        object so clients can inspect it programmatically.

    What this shows:
        - Response payloads are JSON dicts keyed by model name.
        - Diagnostics are suitable for automation.

    Best practice:
        Validate payload shapes for diagnostics endpoints to keep tooling
        robust across changes.
    """

    # Setup: declare a model for payload shape validation.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_kernel_shape_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    # Deployment: create the app and attach diagnostics at root.
    app = TigrblApp(engine=mem(async_=False), system_prefix="")
    app.include_model(Widget)
    app.initialize()
    app.attach_diagnostics()

    # Deployment: run the app under Uvicorn.
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    # Test: request the kernel diagnostics payload.
    async with httpx.AsyncClient(base_url=handle.base_url, timeout=10.0) as client:
        response = await client.get("/kernelz")
        assert response.status_code == 200
        payload = response.json()
        # Assertion: the payload is JSON object for tooling consumption.
        assert isinstance(payload, dict)
    await stop_server(handle)
