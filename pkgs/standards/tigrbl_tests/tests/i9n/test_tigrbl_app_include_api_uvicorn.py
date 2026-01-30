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
    __tablename__ = "alpha_widgets_alt"
    __resource__ = "alpha-widget"

    name: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("create", "read", "list")),
    )


class BetaWidget(Base, GUIDPk):
    __tablename__ = "beta_widgets_alt"
    __resource__ = "beta-widget"

    name: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("create", "read", "list")),
    )


class ZetaWidget(Base, GUIDPk):
    __tablename__ = "zeta_widgets_alt"
    __resource__ = "zeta-widget"

    name: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("create", "read", "list")),
    )


@pytest_asyncio.fixture()
async def running_app_with_apis():
    engine = mem(async_=False)
    alpha_api = TigrblApi(engine=engine, models=[AlphaWidget], prefix="/alpha")
    beta_api = TigrblApi(engine=engine)
    beta_api.include_model(BetaWidget)
    zeta_api = TigrblApi(engine=engine)
    zeta_api.include_model(ZetaWidget)

    app = TigrblApp(engine=engine, apis=[alpha_api, (zeta_api, "/zeta")])
    app.include_api(beta_api, prefix="/beta")
    await app.initialize()

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        yield base_url
    finally:
        await stop_uvicorn_server(server, task)


@pytest_asyncio.fixture()
async def running_app_with_api_router():
    engine = mem(async_=False)
    alpha_api = TigrblApi(engine=engine)
    alpha_api.include_model(AlphaWidget)
    beta_api = TigrblApi(engine=engine)
    beta_api.include_model(BetaWidget)

    app = TigrblApp(engine=engine, apis=[alpha_api])
    app.include_api(beta_api, prefix="/beta")
    app.include_api(alpha_api.router, prefix="/alpha")
    await app.initialize()

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        yield base_url
    finally:
        await stop_uvicorn_server(server, task)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrbl_app_api_list_alpha(running_app_with_apis):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{running_app_with_apis}/alpha/alpha-widget", json={"name": "ace"}
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "ace"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrbl_app_include_api_beta(running_app_with_apis):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{running_app_with_apis}/beta/beta-widget", json={"name": "bolt"}
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "bolt"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrbl_app_api_list_zeta(running_app_with_apis):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{running_app_with_apis}/zeta/zeta-widget", json={"name": "zen"}
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "zen"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrbl_app_include_api_router_alpha(running_app_with_api_router):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{running_app_with_api_router}/alpha/alpha-widget", json={"name": "ace"}
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "ace"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrbl_app_include_api_router_beta(running_app_with_api_router):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{running_app_with_api_router}/beta/beta-widget", json={"name": "bolt"}
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "bolt"
