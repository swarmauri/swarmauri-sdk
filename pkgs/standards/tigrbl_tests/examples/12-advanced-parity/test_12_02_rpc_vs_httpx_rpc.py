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
async def test_rpc_parity_with_httpx() -> None:
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_rpc_parity_widget"
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
        client = TigrblClient(f"{base_url}/rpc")

        rpc_result = client.call("Widget.create", params={"name": "RPC"})

        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as http_client:
            payload = {
                "jsonrpc": "2.0",
                "method": "Widget.create",
                "params": {"name": "RPC"},
                "id": "1",
            }
            http_result = await http_client.post("/rpc", json=payload)

        assert http_result.status_code == 200
        assert http_result.json()["result"]["name"] == rpc_result["name"]
    finally:
        await stop_uvicorn(server, task)
