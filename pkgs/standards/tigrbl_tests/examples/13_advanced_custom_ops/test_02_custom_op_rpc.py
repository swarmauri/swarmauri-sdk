import pytest
from tigrbl import Base, TigrblApp, op_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String
from tigrbl_client import TigrblClient

from examples._support import pick_unused_port, run_uvicorn_app, stop_server


@pytest.mark.asyncio
async def test_custom_op_via_rpc():
    """Teach calling a custom op through the JSON-RPC interface.

    Purpose:
        Validate that a custom op is exposed through the RPC endpoint and can
        be invoked by name.

    What this shows:
        - RPC methods use the ``Model.op`` naming convention.
        - Custom ops can return structured data to clients.

    Best practice:
        Keep custom op outputs structured (lists/dicts) to stay compatible with
        both RPC and REST workflows.
    """

    # Setup: declare a model with a custom RPC op.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_custom_rpc_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    @op_ctx(alias="ping", target="custom", arity="collection")
    def ping(cls, ctx):
        return [{"ok": True}]

    # Setup: attach the op to the model.
    Widget.ping = ping

    # Deployment: create an API, mount JSON-RPC, and attach diagnostics for healthz.
    app = TigrblApp(engine=mem(async_=False), system_prefix="")
    app.include_model(Widget)
    app.initialize()
    app.mount_jsonrpc(prefix="/rpc")
    app.attach_diagnostics()

    # Deployment: run the app under Uvicorn.
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)

    # Test: call the custom op via JSON-RPC.
    client = TigrblClient(handle.base_url + "/rpc")
    result = await client.acall(f"{Widget.__name__}.ping", params={})

    # Assertion: the RPC response contains the expected payload.
    assert result[0]["ok"] is True
    await client.aclose()
    await stop_server(handle)


@pytest.mark.asyncio
async def test_custom_rpc_op_returns_expected_payload_shape():
    """Reinforce that custom RPC ops return predictable payload shapes.

    Purpose:
        Ensure the returned payload is a list of dictionaries so clients can
        iterate reliably.

    What this shows:
        - RPC calls return the op output unchanged.
        - Payload shapes stay consistent for custom operations.

    Best practice:
        Favor list-based responses for collection-level custom ops to align
        with other collection endpoints.
    """

    # Setup: declare a model with a custom op that returns a list payload.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_custom_rpc_payload_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    @op_ctx(alias="pong", target="custom", arity="collection")
    def pong(cls, ctx):
        return [{"ok": "pong"}]

    # Setup: attach the op to the model.
    Widget.pong = pong

    # Deployment: create an API, mount JSON-RPC, and attach diagnostics.
    app = TigrblApp(engine=mem(async_=False), system_prefix="")
    app.include_model(Widget)
    app.initialize()
    app.mount_jsonrpc(prefix="/rpc")
    app.attach_diagnostics()

    # Deployment: run the app under Uvicorn.
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)

    # Test: call the RPC op and inspect the payload shape.
    client = TigrblClient(handle.base_url + "/rpc")
    result = await client.acall(f"{Widget.__name__}.pong", params={})

    # Assertion: the payload is list-based with the expected value.
    assert isinstance(result, list)
    assert result[0]["ok"] == "pong"
    await client.aclose()
    await stop_server(handle)
