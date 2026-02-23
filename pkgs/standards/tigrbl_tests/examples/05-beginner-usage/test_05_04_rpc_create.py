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
async def test_rpc_create_via_client() -> None:
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_rpc_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)
    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    app.mount_jsonrpc(prefix="/rpc")

    app.attach_diagnostics(prefix="", app=app)

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        client = TigrblClient(f"{base_url}/rpc")
        result = await client.acall("Widget.create", params={"name": "Bravo"})
        assert result["name"] == "Bravo"
    finally:
        await stop_uvicorn(server, task)
