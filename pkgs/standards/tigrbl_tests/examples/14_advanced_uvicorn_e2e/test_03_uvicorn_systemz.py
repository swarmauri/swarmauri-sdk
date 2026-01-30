import httpx
import pytest
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String

from examples._support import pick_unused_port, run_uvicorn_app, stop_server


@pytest.mark.asyncio
async def test_uvicorn_systemz_route():
    """Teach attaching a custom system route alongside diagnostics.

    Purpose:
        Verify that a custom system route can coexist with diagnostics routes
        and still respond under Uvicorn.

    What this shows:
        - APIs can register additional system endpoints.
        - Diagnostics attachment does not override custom routes.

    Best practice:
        Keep system endpoints explicit and minimal to avoid mixing them with
        resource routes.
    """

    # Setup: define a model to mount alongside system routes.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_system_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    # Deployment: create the app, include the model, and add a system route.
    app = TigrblApp(engine=mem(async_=False), system_prefix="")
    app.include_model(Widget)
    app.initialize()
    app.add_api_route("/systemz", lambda: {"system": True}, methods=["GET"])
    app.attach_diagnostics()

    # Deployment: run the app under Uvicorn.
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    # Test: call the custom system route.
    async with httpx.AsyncClient(base_url=handle.base_url, timeout=10.0) as client:
        response = await client.get("/systemz")
        # Assertion: the system endpoint responds successfully.
        assert response.status_code == 200
    await stop_server(handle)


@pytest.mark.asyncio
async def test_uvicorn_systemz_returns_expected_payload():
    """Reinforce that custom system endpoints return stable payloads.

    Purpose:
        Confirm the system route returns the payload defined in the handler so
        consumers can rely on contract stability.

    What this shows:
        - Custom system handlers are executed as defined.
        - JSON responses are preserved end-to-end.

    Best practice:
        Make system payloads explicit and versionable for operational tooling.
    """

    # Setup: define a model for payload validation.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_system_payload_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    # Deployment: create the app, add the system route, and attach diagnostics.
    app = TigrblApp(engine=mem(async_=False), system_prefix="")
    app.include_model(Widget)
    app.initialize()
    app.add_api_route("/systemz", lambda: {"system": True}, methods=["GET"])
    app.attach_diagnostics()

    # Deployment: run the app under Uvicorn.
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    # Test: call the system route and parse JSON.
    async with httpx.AsyncClient(base_url=handle.base_url, timeout=10.0) as client:
        response = await client.get("/systemz")
        assert response.status_code == 200
        # Assertion: the payload matches the handler output.
        assert response.json() == {"system": True}
    await stop_server(handle)
