import inspect

import httpx
import pytest

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import App, Column, String


@pytest.mark.asyncio
async def test_uvicorn_systemz_route():
    """Test uvicorn systemz route."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_system"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    api = TigrblApp(engine=mem(async_=False))
    api.include_model(Widget)
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    app = App()
    app.include_router(api.router)
    app.add_api_route("/systemz", lambda: {"system": True}, methods=["GET"])
    api.attach_diagnostics(prefix="", app=app)
    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        response = await client.get("/systemz")
        assert response.status_code == 200
    await stop_uvicorn(server, task)
