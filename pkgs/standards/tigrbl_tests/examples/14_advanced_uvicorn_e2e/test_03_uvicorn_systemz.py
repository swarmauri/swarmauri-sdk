import inspect

import httpx
import pytest

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblApp, TigrblRouter
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


@pytest.mark.asyncio
async def test_uvicorn_systemz_route():
    """Test uvicorn systemz route."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_system"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

<<<<<<< HEAD
    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)
    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    router = TigrblRouter()
    app.include_router(router)
    app.add_route("/systemz", lambda: {"system": True}, methods=["GET"])
    app.attach_diagnostics(prefix="")
=======
    router = TigrblApp(engine=mem(async_=False))
    router.include_model(Widget)
    init_result = router.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    app = TigrblApp()
    app.include_router(router.router)
    app.add_api_route("/systemz", lambda: {"system": True}, methods=["GET"])
    router.attach_diagnostics(prefix="", app=app)
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        response = await client.get("/systemz")
        assert response.status_code == 200
    await stop_uvicorn(server, task)
