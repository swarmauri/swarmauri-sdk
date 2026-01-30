from __future__ import annotations

import inspect

import httpx
import pytest

from tigrbl_client import TigrblClient

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import App, Column, String


@pytest.mark.asyncio
async def test_rest_and_rpc_ids_align() -> None:
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_rpc_rest_ids"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    api = TigrblApp(engine=mem(async_=False))
    api.include_model(Widget)
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    api.mount_jsonrpc(prefix="/rpc")

    app = App()
    app.include_router(api.router)
    api.attach_diagnostics(prefix="", app=app)

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as http_client:
            rest = await http_client.post("/widget", json={"name": "Mix"})
        rest_id = rest.json()["id"]

        client = TigrblClient(f"{base_url}/rpc")
        rpc = client.call("Widget.read", params={"id": rest_id})

        assert rpc["id"] == rest_id
    finally:
        await stop_uvicorn(server, task)
