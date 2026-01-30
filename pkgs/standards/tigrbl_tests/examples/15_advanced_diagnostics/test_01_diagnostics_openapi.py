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
async def test_diagnostics_show_in_openapi_schema():
    Widget = build_widget_model("LessonDiagOpenAPI")
    app, _ = build_app_with_jsonrpc_and_diagnostics(Widget)
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    async with build_async_client(handle.base_url) as client:
        response = await client.get("/openapi.json")
        assert "/healthz" in response.json()["paths"]
        assert "/kernelz" in response.json()["paths"]
    await stop_server(handle)
