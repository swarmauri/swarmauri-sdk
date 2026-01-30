import inspect

import httpx
import pytest
from tigrbl import Base, TigrblApp, hook_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import App, Column, String

from examples._support import (
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

    class LessonHookz(Base, GUIDPk):
        __tablename__ = "lessonhookzs"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonHookz
    Widget.audit = audit

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
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    async with httpx.AsyncClient(base_url=handle.base_url, timeout=10.0) as client:
        response = await client.get("/hookz")
        assert response.status_code == 200
    await stop_server(handle)
