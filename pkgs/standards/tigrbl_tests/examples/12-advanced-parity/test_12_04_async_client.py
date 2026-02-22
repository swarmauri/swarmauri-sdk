from __future__ import annotations

import inspect

import pytest

from tigrbl_client import TigrblClient

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


@pytest.mark.asyncio
async def test_async_client_get() -> None:
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_async_client_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    router = TigrblApp(engine=mem(async_=False))
    router.include_model(Widget)
    init_result = router.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    app = TigrblApp()
    app.include_router(router.router)
    router.attach_diagnostics(prefix="", app=app)

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        client = TigrblClient(base_url)
        created = await client.apost("/widget", data={"name": "Async"})
        item_id = created["id"]
        response = await client.aget(f"/widget/{item_id}")
        assert response["name"] == "Async"
    finally:
        await stop_uvicorn(server, task)
