import inspect

import httpx
import pytest
from tigrbl import Base, TigrblApp, hook_ctx

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import App, Column, String


@pytest.mark.asyncio
async def test_diagnostics_hookz_reports_hooks():
    """Test diagnostics hookz reports hooks."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_hookz"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="POST_COMMIT")
        def audit(cls, ctx):
            return None

    api = TigrblApp(engine=mem(async_=False))
    api.include_model(Widget)
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    api.mount_jsonrpc(prefix="/rpc")

    app = App()
    app.include_router(api.router)
    api.attach_diagnostics(prefix="", app=app)

    api.bind(Widget)
    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        response = await client.get("/hookz")
        assert response.status_code == 200
    await stop_uvicorn(server, task)
