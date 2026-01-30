import pytest

from tigrbl.types import App
from examples._support import (
    build_simple_api,
    build_async_client,
    build_widget_model,
    pick_unused_port,
    run_uvicorn_app,
    stop_server,
)


@pytest.mark.asyncio
async def test_uvicorn_systemz_route():
    Widget = build_widget_model("LessonSystem")
    api = build_simple_api(Widget)
    app = App()
    app.include_router(api.router)
    app.add_api_route("/systemz", lambda: {"system": True}, methods=["GET"])
    api.attach_diagnostics(prefix="", app=app)
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    async with build_async_client(handle.base_url) as client:
        response = await client.get("/systemz")
        assert response.status_code == 200
    await stop_server(handle)
