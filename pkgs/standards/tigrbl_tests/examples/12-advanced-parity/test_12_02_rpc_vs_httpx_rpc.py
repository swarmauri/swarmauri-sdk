from __future__ import annotations

import inspect

import httpx
import pytest

from tigrbl_client import TigrblClient

from tigrbl_tests.examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import TableBase, TigrblApp, TigrblRouter
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


@pytest.mark.asyncio
async def test_rpc_parity_with_httpx() -> None:
    class Widget(TableBase, GUIDPk):
        __tablename__ = "lesson_rpc_parity_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    router = TigrblRouter(engine=mem(async_=False))
    router.include_table(Widget)
    init_result = router.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    router.mount_jsonrpc(prefix="/rpc")

    app = TigrblApp()
    app.include_router(router)
    app.attach_diagnostics(prefix="")

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        client = TigrblClient(f"{base_url}/rpc")

        rpc_result = await client.acall("Widget.create", params={"name": "RPC"})

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
