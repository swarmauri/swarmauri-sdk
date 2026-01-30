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
async def test_rest_update_round_trip() -> None:
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_update_widget"
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
            create = await client.post("/widget", json={"name": "Gamma"})
            item_id = create.json()["id"]
            update = await client.patch(
                f"/widget/{item_id}",
                json={"name": "Delta"},
            )
            assert update.status_code == 200
            assert update.json()["name"] == "Delta"
    finally:
        await stop_uvicorn(server, task)
