import inspect

import httpx
import pytest
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import App, Column, String

from examples._support import (
    pick_unused_port,
    run_uvicorn_app,
    stop_server,
)


@pytest.mark.asyncio
async def test_kernelz_returns_operation_plan():
    """Test kernelz returns operation plan."""

    class LessonKernelz(Base, GUIDPk):
        __tablename__ = "lessonkernelzs"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonKernelz
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
        response = await client.get("/kernelz")
        assert response.status_code == 200
        payload = response.json()
        assert Widget.__name__ in payload
    await stop_server(handle)
