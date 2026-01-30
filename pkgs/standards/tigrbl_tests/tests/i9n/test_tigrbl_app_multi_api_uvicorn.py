import httpx
import pytest
import pytest_asyncio

from tigrbl import Base, TigrblApi, TigrblApp
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
async def running_multi_api_app():
    engine = mem(async_=False)
    alpha_api = TigrblApi(engine=engine)
    alpha_api.include_model(AlphaWidget)

    beta_api = TigrblApi(engine=engine)
    beta_api.include_model(BetaWidget)

    app = TigrblApp(engine=engine, apis=[alpha_api])
    app.include_router(beta_api, prefix="/beta")
    app.include_router(alpha_api.router, prefix="/alpha")
    await app.initialize()

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        yield base_url
    finally:
        await stop_uvicorn_server(server, task)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrbl_app_routes_alpha_api(running_multi_api_app):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{running_multi_api_app}/alpha/alpha-widget", json={"name": "ace"}
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "ace"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrbl_app_routes_beta_api(running_multi_api_app):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{running_multi_api_app}/beta/beta-widget", json={"name": "bolt"}
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "bolt"
