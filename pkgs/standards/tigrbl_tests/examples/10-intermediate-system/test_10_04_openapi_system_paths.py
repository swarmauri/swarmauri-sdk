from __future__ import annotations

import inspect

import httpx
import pytest

from tigrbl_tests.examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import TableBase, TigrblApp, TigrblRouter
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


@pytest.mark.asyncio
async def test_openapi_system_paths() -> None:
    class Widget(TableBase, GUIDPk):
        __tablename__ = "lesson_openapi_system_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    router = TigrblRouter(engine=mem(async_=False), system_prefix="/systemz")
    router.include_table(Widget)
    init_result = router.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    app = TigrblApp()
    app.include_router(router)
    app.attach_diagnostics(prefix="")
    app.attach_diagnostics(prefix="/systemz", app=app)

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            response = await client.get("/openapi.json")
        paths = response.json()["paths"]
        assert "/healthz" in paths
        assert "/kernelz" in paths
        assert "/systemz/healthz" in paths
    finally:
        await stop_uvicorn(server, task)
