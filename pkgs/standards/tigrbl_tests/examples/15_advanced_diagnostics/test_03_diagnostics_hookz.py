import pytest
from tigrbl import hook_ctx

from examples._support import (
    build_app_with_jsonrpc_and_diagnostics,
    build_async_client,
    build_widget_model,
    pick_unused_port,
    run_uvicorn_app,
    stop_server,
)


@pytest.mark.asyncio
async def test_diagnostics_hookz_reports_hooks():
    """Test diagnostics hookz reports hooks."""

    @hook_ctx(ops="create", phase="POST_COMMIT")
    def audit(cls, ctx):
        return None

    Widget = build_widget_model("LessonHookz", extra_attrs={"audit": audit})

    app, api = build_app_with_jsonrpc_and_diagnostics(Widget)
    api.bind(Widget)
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    async with build_async_client(handle.base_url) as client:
        response = await client.get("/hookz")
        assert response.status_code == 200
    await stop_server(handle)
