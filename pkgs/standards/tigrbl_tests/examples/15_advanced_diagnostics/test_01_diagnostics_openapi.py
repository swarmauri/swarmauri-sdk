import inspect

import httpx
import pytest

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


@pytest.mark.asyncio
async def test_diagnostics_show_in_openapi_schema():
    """Test diagnostics show in openapi schema."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_diag_openapi"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    router = TigrblApp(engine=mem(async_=False))
    router.include_model(Widget)
    init_result = router.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    router.mount_jsonrpc(prefix="/rpc")

    app = TigrblApp()
    app.include_router(router.router)
    router.attach_diagnostics(prefix="", app=app)

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        response = await client.get("/openapi.json")
        assert "/healthz" in response.json()["paths"]
        assert "/kernelz" in response.json()["paths"]
    await stop_uvicorn(server, task)
