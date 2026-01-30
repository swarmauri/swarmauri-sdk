import httpx
import pytest
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String

from examples._support import pick_unused_port, run_uvicorn_app, stop_server


@pytest.mark.asyncio
async def test_diagnostics_show_in_openapi_schema():
    """Teach how diagnostics endpoints appear in OpenAPI.

    Purpose:
        Ensure diagnostics routes are included in the generated OpenAPI schema
        so tooling can discover them.

    What this shows:
        - Diagnostics endpoints are part of the FastAPI app.
        - OpenAPI reflects system routes like ``/healthz`` and ``/kernelz``.

    Best practice:
        Keep diagnostics documented so operators can introspect available
        endpoints consistently.
    """

    # Setup: define a model to expose diagnostics in OpenAPI.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_diag_openapi_widgets"
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
    # Test: fetch the OpenAPI schema.
    async with httpx.AsyncClient(base_url=handle.base_url, timeout=10.0) as client:
        response = await client.get("/openapi.json")
        # Assertion: diagnostics endpoints are documented.
        assert "/healthz" in response.json()["paths"]
        assert "/kernelz" in response.json()["paths"]
    await stop_server(handle)


@pytest.mark.asyncio
async def test_openapi_includes_methodz_and_hookz_paths():
    """Reinforce that diagnostic discovery endpoints are documented.

    Purpose:
        Confirm that method and hook listings are part of the OpenAPI schema.

    What this shows:
        - ``/methodz`` and ``/hookz`` are exposed for inspection.
        - Operators can locate diagnostics via standard tooling.

    Best practice:
        Document diagnostic endpoints to keep observability self-service.
    """

    # Setup: define a model for diagnostics path checks.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_diag_paths_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    # Deployment: create the app and attach diagnostics at the root.
    app = TigrblApp(engine=mem(async_=False), system_prefix="")
    app.include_model(Widget)
    app.initialize()
    app.attach_diagnostics()

    # Deployment: run the app under Uvicorn.
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    # Test: request the OpenAPI schema and inspect paths.
    async with httpx.AsyncClient(base_url=handle.base_url, timeout=10.0) as client:
        response = await client.get("/openapi.json")
        paths = response.json()["paths"]
        # Assertion: method and hook diagnostics are documented.
        assert "/methodz" in paths
        assert "/hookz" in paths
    await stop_server(handle)
