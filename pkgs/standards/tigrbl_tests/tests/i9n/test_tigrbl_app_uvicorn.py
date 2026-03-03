import httpx
import pytest
import pytest_asyncio
import tempfile
import os
import contextlib
from tigrbl import TableBase, TigrblApp
from tigrbl.shortcuts.engine import sqlitef
from tigrbl.orm.mixins import GUIDPk
from tigrbl._spec import IO, F, S, acol
from tigrbl.types import Mapped, String

from .uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server


class Widget(TableBase, GUIDPk):
    __tablename__ = "widgets_app"
    __resource__ = "widget"

    name: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("create", "read", "list")),
    )


@pytest_asyncio.fixture()
async def running_app():
    db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_file.close()
    app = TigrblApp(engine=sqlitef(db_file.name, async_=False))
    app.include_table(Widget)
    app.attach_diagnostics()
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
async def test_tigrbl_app_create_widget(running_app):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{running_app}/widget", json={"name": "alpha"})

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "alpha"
    assert "id" in payload


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrbl_app_healthz(running_app):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{running_app}/system/healthz")

    assert response.status_code == 200
    assert response.json()["ok"] is True
