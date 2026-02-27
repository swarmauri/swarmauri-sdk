import inspect

import httpx
import pytest
from tigrbl import Base, TigrblApp, TigrblRouter
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String
from tigrbl_tests.examples._support import pick_unique_port, start_uvicorn, stop_uvicorn


@pytest.mark.asyncio
async def test_diagnostics_show_in_openapi_schema():
    """Test diagnostics show in openapi schema."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_diag_openapi"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

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
        response = await client.get("/openapi.json")
        assert "/healthz" in response.json()["paths"]
        assert "/kernelz" in response.json()["paths"]
    await stop_uvicorn(server, task)
