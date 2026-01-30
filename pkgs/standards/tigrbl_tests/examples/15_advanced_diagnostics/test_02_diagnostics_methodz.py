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
async def test_diagnostics_methodz_lists_operations():
    """Test diagnostics methodz lists operations."""
    Widget = build_widget_model("LessonMethodz")
    app, _ = build_app_with_jsonrpc_and_diagnostics(Widget)
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    async with build_async_client(handle.base_url) as client:
        response = await client.get("/methodz")
        assert response.status_code == 200
        methods = {entry["method"] for entry in response.json()["methods"]}
        assert f"{Widget.__name__}.list" in methods
    await stop_server(handle)
