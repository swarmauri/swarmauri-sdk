import httpx
import pytest
import pytest_asyncio

from tigrbl import Base, TigrblRouter, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import Mapped, String

from .uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server


class AlphaWidget(Base, GUIDPk):
    __tablename__ = "alpha_widgets"
    __resource__ = "alpha-widget"

    name: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("create", "read", "list")),
    )


class BetaWidget(Base, GUIDPk):
    __tablename__ = "beta_widgets"
    __resource__ = "beta-widget"

    name: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("create", "read", "list")),
    )


@pytest_asyncio.fixture()
async def running_multi_router_app():
    engine = mem(async_=False)
    routers = [TigrblRouter(engine=engine), TigrblRouter(engine=engine)]
    router = routers[0]
    router.include_table(AlphaWidget)

    routers[1].include_table(BetaWidget)

    app = TigrblApp(engine=engine, routers=[router])
    app.include_router(routers[1], prefix="/beta")
    app.include_router(router.router, prefix="/alpha")
    await app.initialize()

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        yield base_url
    finally:
        await stop_uvicorn_server(server, task)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrbl_app_routes_alpha_router(running_multi_router_app):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{running_multi_router_app}/alpha/alpha-widget", json={"name": "ace"}
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "ace"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrbl_app_routes_beta_router(running_multi_router_app):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{running_multi_router_app}/beta/beta-widget", json={"name": "bolt"}
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "bolt"
