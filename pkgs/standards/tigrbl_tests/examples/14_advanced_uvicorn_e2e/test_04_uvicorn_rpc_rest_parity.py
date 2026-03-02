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
async def test_rpc_and_rest_parity_with_uvicorn():
    """Test rpc and rest parity with uvicorn."""

    class Widget(TableBase, GUIDPk):
        __tablename__ = "lesson_parity"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)
    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    app.mount_jsonrpc(prefix="/rpc")

    router = TigrblRouter()
    app.include_router(router)
    app.attach_diagnostics(prefix="")

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        response = await client.post(
            f"/{Widget.__name__.lower()}",
            json={"name": "gamma"},
        )
        assert response.status_code in {200, 201}

    rpc_client = TigrblClient(base_url + "/rpc")
    rpc_response = await rpc_client.acall(f"{Widget.__name__}.list", params={})
    items = (
        rpc_response.get("items") if isinstance(rpc_response, dict) else rpc_response
    )
    assert items
    assert items[0]["name"] == "gamma"
    await rpc_client.aclose()
    await stop_uvicorn(server, task)
