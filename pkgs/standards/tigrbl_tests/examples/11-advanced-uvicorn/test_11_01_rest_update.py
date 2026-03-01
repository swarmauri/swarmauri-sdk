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
async def test_rest_update_round_trip() -> None:
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_update_widget"
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
