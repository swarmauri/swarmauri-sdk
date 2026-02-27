from __future__ import annotations

import inspect

import httpx
import pytest

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl.concrete.tigrbl_app import TigrblApp
from tigrbl.router import TigrblRouter
from tigrbl.table import Base
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


@pytest.mark.asyncio
async def test_kernelz_includes_widget() -> None:
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_kernelz_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)
    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    router = TigrblRouter()
    app.include_router(router)
    app.attach_diagnostics(prefix="")

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            kernelz = await client.get("/kernelz")
        assert kernelz.status_code == 200
        assert "Widget" in kernelz.json()
    finally:
        await stop_uvicorn(server, task)
