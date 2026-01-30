import pytest

from examples._support import (
    build_app_with_jsonrpc_and_diagnostics,
    build_async_client,
    build_widget_model,
    pick_unused_port,
    run_uvicorn_app,
    stop_server,
)


@pytest.mark.asyncio
async def test_kernelz_returns_operation_plan():
    """Test kernelz returns operation plan."""
    Widget = build_widget_model("LessonKernelz")
    app, _ = build_app_with_jsonrpc_and_diagnostics(Widget)
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    async with build_async_client(handle.base_url) as client:
        response = await client.get("/kernelz")
        assert response.status_code == 200
        payload = response.json()
        assert Widget.__name__ in payload
    await stop_server(handle)
