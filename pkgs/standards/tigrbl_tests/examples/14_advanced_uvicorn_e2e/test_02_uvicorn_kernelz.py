import httpx
import pytest
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String

from examples._support import pick_unused_port, run_uvicorn_app, stop_server


@pytest.mark.asyncio
async def test_uvicorn_kernelz_endpoint():
    """Explain the diagnostics kernel endpoint.

    Purpose:
        Ensure that ``/kernelz`` is reachable and returns a response when the
        server is running.

    What this shows:
        - Kernel diagnostics are mounted alongside the main API.
        - Kernel output is accessible without extra configuration.

    Best practice:
        Keep diagnostics endpoints enabled in non-production environments to
        help inspect operation plans.
    """

    # Setup: declare a model for kernel diagnostics.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_kernel_widgets"
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
    # Test: call the kernel diagnostics endpoint.
    async with httpx.AsyncClient(base_url=handle.base_url, timeout=10.0) as client:
        response = await client.get("/kernelz")
        # Assertion: the endpoint responds successfully.
        assert response.status_code == 200
    await stop_server(handle)


@pytest.mark.asyncio
async def test_uvicorn_kernelz_includes_model_name():
    """Reinforce that kernel output is model-aware.

    Purpose:
        Validate that the kernel diagnostics payload references the model by
        name, confirming that the API registered the model.

    What this shows:
        - Kernel payloads include model keys.
        - The diagnostics layer mirrors the API registry.

    Best practice:
        Use kernel diagnostics to verify model registration during debugging.
    """

    # Setup: declare a model to verify kernel payload contents.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_kernel_model_widgets"
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
        # Assertion: the model name is present in the diagnostics payload.
        assert Widget.__name__ in payload
    await stop_server(handle)
