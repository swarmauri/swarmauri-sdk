import pytest
from tigrbl_client import TigrblClient

from examples._support import (
    build_app_with_jsonrpc_and_diagnostics,
    build_widget_model,
    pick_unused_port,
    run_uvicorn_app,
    stop_server,
)


@pytest.mark.asyncio
async def test_rpc_call_works_over_jsonrpc():
    """Test rpc call works over jsonrpc."""
    Widget = build_widget_model("LessonRPCClient")
    app, _ = build_app_with_jsonrpc_and_diagnostics(Widget)
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)

    client = TigrblClient(handle.base_url + "/rpc")
    result = await client.acall(f"{Widget.__name__}.list", params={})
    assert isinstance(result, list)
    await client.aclose()
    await stop_server(handle)
