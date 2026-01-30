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
async def test_diagnostics_show_in_openapi_schema():
    """Test diagnostics show in openapi schema."""

    class LessonDiagOpenAPI(Base, GUIDPk):
        __tablename__ = "lessondiagopenapis"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonDiagOpenAPI
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
        response = await client.get("/openapi.json")
        assert "/healthz" in response.json()["paths"]
        assert "/kernelz" in response.json()["paths"]
    await stop_server(handle)
