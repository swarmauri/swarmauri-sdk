import inspect

import pytest
from tigrbl import Base, TigrblApp, op_ctx
from tigrbl_client import TigrblClient

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import App, Column, String


@pytest.mark.asyncio
async def test_custom_op_via_rpc():
    """Test custom op via rpc."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_custom_rpc"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

        @op_ctx(alias="ping", target="custom", arity="collection")
        def ping(cls, ctx):
            return [{"ok": True}]

    api = TigrblApp(engine=mem(async_=False))
    api.include_model(Widget)
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    api.mount_jsonrpc(prefix="/rpc")

    app = App()
    app.include_router(api.router)
    api.attach_diagnostics(prefix="", app=app)

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)

    client = TigrblClient(base_url + "/rpc")
    result = await client.acall(f"{Widget.__name__}.ping", params={})
    assert result[0]["ok"] is True
    await client.aclose()
    await stop_uvicorn(server, task)
