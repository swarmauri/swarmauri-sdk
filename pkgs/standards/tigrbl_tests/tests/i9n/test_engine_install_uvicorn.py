import httpx
import pytest
import pytest_asyncio

from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import Mapped, String

from .uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server


class EngineWidget(Base, GUIDPk):
    __tablename__ = "engine_widgets"

    name: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("read", "list")),
    )


@pytest_asyncio.fixture()
async def running_engine_app():
    app = TigrblApp(engine=mem(async_=False))
    app.include_model(EngineWidget)
    app.mount_jsonrpc(prefix="/rpc")
    app.initialize()

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        yield base_url
    finally:
        await stop_uvicorn_server(server, task)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_engine_server_rest_and_jsonrpc_calls(running_engine_app) -> None:
    base_url = running_engine_app

    async with httpx.AsyncClient() as client:
        rest_resp = await client.post(
            f"{base_url}/enginewidget",
            json={"name": "Alpha"},
        )
        assert rest_resp.status_code == 201
        payload = rest_resp.json()
        assert payload["name"] == "Alpha"

        rpc_payload = {
            "jsonrpc": "2.0",
            "method": "EngineWidget.list",
            "params": {},
            "id": 1,
        }
        rpc_resp = await client.post(f"{base_url}/rpc", json=rpc_payload)

    assert rpc_resp.status_code == 200
    results = rpc_resp.json()["result"]
    assert any(item["name"] == "Alpha" for item in results)
