import httpx
import pytest
from tigrbl import Base, TigrblApp, op_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String

from examples._support import pick_unused_port, run_uvicorn_app, stop_server


@pytest.mark.asyncio
async def test_custom_op_exposed_on_rest_routes():
    """Teach exposing a custom op as a REST route.

    Purpose:
        Verify that a custom op is mounted as a REST endpoint with the expected
        URL shape.

    What this shows:
        - Custom ops become POST routes under the model path.
        - REST clients can invoke ops without RPC tooling.

    Best practice:
        Keep REST custom ops in the model namespace to maintain route clarity.
    """

    # Setup: declare a model with a custom REST op.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_custom_rest_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    @op_ctx(alias="status", target="custom", arity="collection")
    def status(cls, ctx):
        return [{"status": "ok"}]

    # Setup: attach the op to the model.
    Widget.status = status

    # Deployment: create the API, attach diagnostics for healthz, and run.
    app = TigrblApp(engine=mem(async_=False), system_prefix="")
    app.include_model(Widget)
    app.initialize()
    app.attach_diagnostics()

    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    # Test: call the custom REST op via HTTP.
    async with httpx.AsyncClient(base_url=handle.base_url, timeout=10.0) as client:
        response = await client.post(
            f"/{Widget.__name__.lower()}/status",
            json={},
        )
        # Assertion: the op is reachable and responds successfully.
        assert response.status_code == 200
    await stop_server(handle)


@pytest.mark.asyncio
async def test_custom_op_rest_returns_payload():
    """Reinforce that REST custom ops return explicit payloads.

    Purpose:
        Ensure the JSON response from a custom op matches the return value.

    What this shows:
        - The handler result is serialized directly to JSON.
        - REST clients can rely on predictable payload keys.

    Best practice:
        Return simple, JSON-serializable structures from custom ops to keep
        client parsing straightforward.
    """

    # Setup: declare a model with a custom REST op that returns data.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_custom_rest_payload_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    @op_ctx(alias="status", target="custom", arity="collection")
    def status(cls, ctx):
        return [{"status": "ready"}]

    # Setup: attach the op to the model.
    Widget.status = status

    # Deployment: create the API, attach diagnostics, and run.
    app = TigrblApp(engine=mem(async_=False), system_prefix="")
    app.include_model(Widget)
    app.initialize()
    app.attach_diagnostics()

    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    # Test: call the custom op and inspect the JSON payload.
    async with httpx.AsyncClient(base_url=handle.base_url, timeout=10.0) as client:
        response = await client.post(f"/{Widget.__name__.lower()}/status", json={})
        assert response.status_code == 200
        payload = response.json()
        # Assertion: the response matches the handler return value.
        assert payload[0]["status"] == "ready"
    await stop_server(handle)
