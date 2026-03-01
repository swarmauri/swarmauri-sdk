from __future__ import annotations

import inspect

import httpx
import pytest

from tigrbl_tests.examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import TigrblApp
from tigrbl import TigrblRouter
from tigrbl import Base
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


@pytest.mark.asyncio
async def test_healthz_ok() -> None:
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_healthz_widget"
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
            response = await client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["ok"] is True
    finally:
        await stop_uvicorn(server, task)
