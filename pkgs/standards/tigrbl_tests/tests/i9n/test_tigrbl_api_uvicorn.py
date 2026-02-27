import httpx
import pytest
import pytest_asyncio
from tigrbl import Base, TigrblApp, TigrblRouter
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import IO, F, S, acol
from tigrbl.types import Mapped, String

from .uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server


class Gadget(Base, GUIDPk):
    __tablename__ = "gadgets_api"
    __resource__ = "gadget"

    name: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("create", "read", "list")),
    )


@pytest_asyncio.fixture()
async def running_router_app():
    router = TigrblRouter(
        engine=mem(async_=False),
        tables=[Gadget],
        prefix="/gadgets",
        system_prefix="/diagnostics",
    )
    await router.initialize()

    app = TigrblApp()
    app.include_router(router.router)
    router.attach_diagnostics(app=app)

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        yield base_url
    finally:
        await stop_uvicorn_server(server, task)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrbl_router_create_gadget(running_router_app):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{running_router_app}/gadgets/gadget", json={"name": "gyro"}
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "gyro"
    assert "id" in payload


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrbl_router_healthz(running_router_app):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{running_router_app}/diagnostics/healthz")

    assert response.status_code == 200
    assert response.json()["ok"] is True
