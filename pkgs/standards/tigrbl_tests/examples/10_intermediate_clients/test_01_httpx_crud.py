import pytest

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
async def test_httpx_crud_roundtrip():
    Widget = build_widget_model("LessonHttpx")
    app, _ = build_app_with_jsonrpc_and_diagnostics(Widget)
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    async with build_async_client(handle.base_url) as client:
        response = await client.post(
            model_route(Widget),
            json=build_rest_payload("alpha"),
        )
        assert response.status_code in {200, 201}
    await stop_server(handle)
