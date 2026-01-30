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
async def test_tigrbl_client_matches_httpx_response():
    Widget = build_widget_model("LessonClient")
    app, _ = build_app_with_jsonrpc_and_diagnostics(Widget)
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    async with build_async_client(handle.base_url) as client:
        response = await client.post(
            model_route(Widget),
            json=build_rest_payload("beta"),
        )
        assert response.status_code in {200, 201}

    client = TigrblClient(handle.base_url)
    rest_response = await client.apost(
        model_route(Widget),
        data=build_rest_payload("beta"),
    )
    assert rest_response["name"] == "beta"
    await client.aclose()
    await stop_server(handle)
