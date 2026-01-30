import httpx
import pytest
import pytest_asyncio

from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import Mapped, String

from .uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server


class Widget(Base, GUIDPk):
    __tablename__ = "widgets_app"
    __resource__ = "widget"

    name: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("create", "read", "list")),
    )


@pytest_asyncio.fixture()
async def running_app():
    app = TigrblApp(engine=mem(async_=False))
    app.include_model(Widget)
    app.attach_diagnostics()
    await app.initialize()

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        yield base_url
    finally:
        await stop_uvicorn_server(server, task)


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
