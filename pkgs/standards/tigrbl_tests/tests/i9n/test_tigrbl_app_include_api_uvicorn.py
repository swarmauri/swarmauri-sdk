import httpx
import pytest
import pytest_asyncio
from tigrbl import TableBase, TigrblApp, TigrblRouter
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl._spec import IO, F, S
from tigrbl.shortcuts.column import acol
from tigrbl.types import Mapped, String

from .uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server


class AlphaWidget(TableBase, GUIDPk):
    __tablename__ = "alpha_widgets_alt"
    __resource__ = "alpha-widget"

    name: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("create", "read", "list")),
    )


class BetaWidget(TableBase, GUIDPk):
    __tablename__ = "beta_widgets_alt"
    __resource__ = "beta-widget"

    name: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("create", "read", "list")),
    )


class ZetaWidget(TableBase, GUIDPk):
    __tablename__ = "zeta_widgets_alt"
    __resource__ = "zeta-widget"

    name: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("create", "read", "list")),
    )


@pytest_asyncio.fixture()
async def running_app_with_routers():
    engine = mem(async_=False)
    router = TigrblRouter(engine=engine, tables=[AlphaWidget], prefix="/alpha")

    app = TigrblApp(engine=engine, routers=[router])

    router = TigrblRouter(engine=engine)
    router.include_table(BetaWidget)
    app.include_router(router, prefix="/beta")

    router = TigrblRouter(engine=engine)
    router.include_table(ZetaWidget)
    app.include_router(router, prefix="/zeta")
    await app.initialize()

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        yield base_url
    finally:
        await stop_uvicorn_server(server, task)


@pytest_asyncio.fixture()
async def running_app_with_router():
    engine = mem(async_=False)
    router = TigrblRouter(engine=engine)
    router.include_table(AlphaWidget)
    alpha_router = router.router

    app = TigrblApp(engine=engine, routers=[router])

    router = TigrblRouter(engine=engine)
    router.include_table(BetaWidget)
    app.include_router(router, prefix="/beta")
    app.include_router(alpha_router, prefix="/alpha")
    await app.initialize()

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        yield base_url
    finally:
        await stop_uvicorn_server(server, task)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrbl_app_router_list_alpha(running_app_with_routers):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{running_app_with_routers}/alpha/alpha-widget", json={"name": "ace"}
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "ace"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrbl_app_include_router_beta(running_app_with_routers):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{running_app_with_routers}/beta/beta-widget", json={"name": "bolt"}
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "bolt"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrbl_app_router_list_zeta(running_app_with_routers):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{running_app_with_routers}/zeta/zeta-widget", json={"name": "zen"}
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "zen"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrbl_app_include_router_alpha(running_app_with_router):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{running_app_with_router}/alpha/alpha-widget", json={"name": "ace"}
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "ace"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrbl_app_include_router_beta_single(running_app_with_router):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{running_app_with_router}/beta/beta-widget", json={"name": "bolt"}
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "bolt"
