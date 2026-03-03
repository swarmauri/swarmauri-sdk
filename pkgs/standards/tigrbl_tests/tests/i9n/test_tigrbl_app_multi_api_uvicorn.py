import httpx
import pytest
import pytest_asyncio
import tempfile
import os
import contextlib
from tigrbl import TableBase, TigrblApp, TigrblRouter
from tigrbl.shortcuts.engine import sqlitef
from tigrbl.orm.mixins import GUIDPk
from tigrbl._spec import IO, F, S, acol
from tigrbl.types import Mapped, String

from .uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server


class AlphaWidget(TableBase, GUIDPk):
    __tablename__ = "alpha_widgets"
    __resource__ = "alpha-widget"

    name: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("create", "read", "list")),
    )


class BetaWidget(TableBase, GUIDPk):
    __tablename__ = "beta_widgets"
    __resource__ = "beta-widget"

    name: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("create", "read", "list")),
    )


@pytest_asyncio.fixture()
async def running_multi_router_app():
    db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_file.close()
    engine = sqlitef(db_file.name, async_=False)

    app = TigrblApp(engine=engine)

    router = TigrblRouter(engine=engine)
    router.include_table(AlphaWidget)
    app.include_router(router.router, prefix="/alpha")

    router = TigrblRouter(engine=engine)
    router.include_table(BetaWidget)
    app.include_router(router, prefix="/beta")

    await app.initialize()

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        yield base_url
    finally:
        await stop_uvicorn_server(server, task)
        with contextlib.suppress(OSError):
            os.unlink(db_file.name)


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
