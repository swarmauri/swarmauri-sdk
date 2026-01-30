import inspect

import httpx
import pytest
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl_client import TigrblClient
from tigrbl.types import App, Column, String

from examples._support import (
    pick_unused_port,
    run_uvicorn_app,
    stop_server,
)


@pytest.mark.asyncio
async def test_rpc_and_rest_parity_with_uvicorn():
    """Test rpc and rest parity with uvicorn."""

    class LessonParity(Base, GUIDPk):
        __tablename__ = "lessonparitys"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonParity
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(Widget)
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    api.mount_jsonrpc(prefix="/rpc")
    app = App()
    app.include_router(api.router)
    api.attach_diagnostics(prefix="", app=app)
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    async with httpx.AsyncClient(base_url=handle.base_url, timeout=10.0) as client:
        response = await client.post(
            f"/{Widget.__name__.lower()}",
            json={"name": "gamma"},
        )
        assert response.status_code in {200, 201}

    rpc_client = TigrblClient(handle.base_url + "/rpc")
    rpc_response = await rpc_client.acall(f"{Widget.__name__}.list", params={})
    items = (
        rpc_response.get("items") if isinstance(rpc_response, dict) else rpc_response
    )
    assert items
    assert items[0]["name"] == "gamma"
    await rpc_client.aclose()
    await stop_server(handle)
