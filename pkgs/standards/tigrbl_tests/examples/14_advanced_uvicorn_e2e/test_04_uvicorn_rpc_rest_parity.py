import pytest
from tigrbl_client import TigrblClient

from examples._support import (
    build_app_with_jsonrpc_and_diagnostics,
    build_async_client,
    build_rest_payload,
    build_widget_model,
    model_route,
    pick_unused_port,
    run_uvicorn_app,
    stop_server,
)


@pytest.mark.asyncio
async def test_rpc_and_rest_parity_with_uvicorn():
    """Test rpc and rest parity with uvicorn."""
    Widget = build_widget_model("LessonParity")
    app, _ = build_app_with_jsonrpc_and_diagnostics(Widget)
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    async with build_async_client(handle.base_url) as client:
        response = await client.post(
            model_route(Widget),
            json=build_rest_payload("gamma"),
        )
        assert response.status_code in {200, 201}

    rpc_client = TigrblClient(handle.base_url + "/rpc")
    rpc_response = await rpc_client.acall(f"{Widget.__name__}.list", params={})
    items = (
        rpc_response.get("items") if isinstance(rpc_response, dict) else rpc_response
    )
    assert items
    assert items[0]["name"] == "gamma"
    await rpc_client.aclose()
    await stop_server(handle)
