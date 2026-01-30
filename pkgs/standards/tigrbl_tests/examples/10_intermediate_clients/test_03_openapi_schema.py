import pytest

from examples._support import (
    build_app_with_jsonrpc_and_diagnostics,
    build_async_client,
    build_widget_model,
    model_route,
    pick_unused_port,
    run_uvicorn_app,
    stop_server,
)


@pytest.mark.asyncio
async def test_openapi_schema_contains_widget_paths():
    Widget = build_widget_model("LessonOpenAPI")
    app, _ = build_app_with_jsonrpc_and_diagnostics(Widget)
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    async with build_async_client(handle.base_url) as client:
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        assert model_route(Widget) in response.json()["paths"]
    await stop_server(handle)
