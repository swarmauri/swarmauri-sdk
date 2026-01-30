import pytest
from tigrbl import op_ctx
from tigrbl_client import TigrblClient

from examples._support import (
    build_app_with_jsonrpc_and_diagnostics,
    build_widget_model,
    pick_unused_port,
    run_uvicorn_app,
    stop_server,
)


@pytest.mark.asyncio
async def test_custom_op_via_rpc():
    Widget = build_widget_model("LessonCustomRpc")

    @op_ctx(alias="ping", target="custom", arity="collection")
    def ping(cls, ctx):
        return [{"ok": True}]

    Widget.ping = ping

    app, _ = build_app_with_jsonrpc_and_diagnostics(Widget)
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)

    client = TigrblClient(handle.base_url + "/rpc")
    result = await client.acall(f"{Widget.__name__}.ping", params={})
    assert result[0]["ok"] is True
    await client.aclose()
    await stop_server(handle)
