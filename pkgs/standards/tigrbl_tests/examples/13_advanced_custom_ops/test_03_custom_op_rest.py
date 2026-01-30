import inspect

import httpx
import pytest
from tigrbl import Base, TigrblApp, op_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import App, Column, String

from examples._support import (
    pick_unused_port,
    run_uvicorn_app,
    stop_server,
)


@pytest.mark.asyncio
async def test_custom_op_exposed_on_rest_routes():
    """Test custom op exposed on rest routes."""

    class LessonCustomRest(Base, GUIDPk):
        __tablename__ = "lessoncustomrests"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonCustomRest

    @op_ctx(alias="status", target="custom", arity="collection")
    def status(cls, ctx):
        return [{"status": "ok"}]

    Widget.status = status

    api = TigrblApp(engine=mem(async_=False))
    api.include_model(Widget)
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    api.mount_jsonrpc(prefix="/rpc")
    app = App()
    app.include_router(api.router)
    api.attach_diagnostics(prefix="", app=app)
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    async with httpx.AsyncClient(base_url=handle.base_url, timeout=10.0) as client:
        response = await client.post(
            f"/{Widget.__name__.lower()}/status",
            json={},
        )
        assert response.status_code == 200
    await stop_server(handle)
