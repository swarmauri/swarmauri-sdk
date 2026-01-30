import httpx
import pytest
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String

from examples._support import pick_unused_port, run_uvicorn_app, stop_server


@pytest.mark.asyncio
async def test_uvicorn_healthz_endpoint():
    """Teach the purpose of the health check endpoint.

    Purpose:
        Verify that ``/healthz`` responds once the Uvicorn server is running.

    What this shows:
        - The diagnostics routes are mounted automatically.
        - Health checks provide a minimal readiness signal.

    Best practice:
        Use a lightweight, dependency-free health check so load balancers can
        probe the service safely.
    """

    # Setup: declare a basic model for the app.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_health_widgets"
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
    # Test: call the health endpoint.
    async with httpx.AsyncClient(base_url=handle.base_url, timeout=10.0) as client:
        response = await client.get("/healthz")
        # Assertion: the endpoint responds successfully.
        assert response.status_code == 200
    await stop_server(handle)


@pytest.mark.asyncio
async def test_uvicorn_healthz_returns_json():
    """Reinforce that health checks return JSON for automation.

    Purpose:
        Confirm that the health endpoint responds with JSON so monitoring tools
        can parse the payload consistently.

    What this shows:
        - Response headers indicate JSON content.
        - The endpoint is suitable for lightweight monitoring.

    Best practice:
        Keep health payloads JSON and compact to aid automation.
    """

    # Setup: declare a model for the health payload check.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_health_json_widgets"
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
    # Test: request the health endpoint and inspect headers.
    async with httpx.AsyncClient(base_url=handle.base_url, timeout=10.0) as client:
        response = await client.get("/healthz")
        assert response.status_code == 200
        # Assertion: the response is JSON for automation tooling.
        assert response.headers["content-type"].startswith("application/json")
    await stop_server(handle)
