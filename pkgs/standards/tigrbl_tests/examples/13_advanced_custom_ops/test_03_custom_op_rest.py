import inspect

import httpx
import pytest
from tigrbl import Base, TigrblApp, op_ctx, TigrblRouter

from tigrbl_tests.examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


@pytest.mark.asyncio
async def test_custom_op_exposed_on_rest_routes():
    """Test custom op exposed on rest routes."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_custom_rest"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

        @op_ctx(alias="status", target="custom", arity="collection")
        def status(cls, ctx):
            return [{"status": "ok"}]

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)
    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    app.mount_jsonrpc(prefix="/rpc")

    router = TigrblRouter()
    app.include_router(router)
    app.attach_diagnostics(prefix="")

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        response = await client.post(
            f"/{Widget.__name__.lower()}/status",
            json={},
        )
        assert response.status_code == 200
    await stop_uvicorn(server, task)
