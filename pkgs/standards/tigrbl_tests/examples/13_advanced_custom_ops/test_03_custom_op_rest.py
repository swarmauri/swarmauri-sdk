import pytest
from tigrbl import op_ctx

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
async def test_custom_op_exposed_on_rest_routes():
    Widget = build_widget_model("LessonCustomRest")

    @op_ctx(alias="status", target="custom", arity="collection")
    def status(cls, ctx):
        return [{"status": "ok"}]

    Widget.status = status

    app, _ = build_app_with_jsonrpc_and_diagnostics(Widget)
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    async with build_async_client(handle.base_url) as client:
        response = await client.post(
            f"{model_route(Widget)}/status",
            json={},
        )
        assert response.status_code == 200
    await stop_server(handle)
