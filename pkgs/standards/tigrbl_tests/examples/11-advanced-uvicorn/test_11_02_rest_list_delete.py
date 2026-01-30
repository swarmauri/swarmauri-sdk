from __future__ import annotations

import inspect

import httpx
import pytest

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import App, Column, String


@pytest.mark.asyncio
async def test_rest_list_and_delete() -> None:
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_list_delete_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    api = TigrblApp(engine=mem(async_=False))
    api.include_model(Widget)
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    app = App()
    app.include_router(api.router)
    api.attach_diagnostics(prefix="", app=app)

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            await client.post("/widget", json={"name": "One"})
            await client.post("/widget", json={"name": "Two"})
            listing = await client.get("/widget")
            assert listing.status_code == 200
            assert len(listing.json()) >= 2
            clear = await client.delete("/widget")
            assert clear.status_code == 200
    finally:
        await stop_uvicorn(server, task)
