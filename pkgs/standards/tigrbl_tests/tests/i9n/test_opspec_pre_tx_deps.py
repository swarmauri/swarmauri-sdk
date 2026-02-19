from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, String

from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.hook import hook_ctx
from tigrbl.op import OpSpec
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import APIRouter
from tigrbl.runtime.status import _RPC_TO_HTTP


async def _build_client(model: type, db_mode: str) -> tuple[AsyncClient, TigrblApp]:
    app = APIRouter()
    api = TigrblApp(engine=mem(async_=(db_mode == "async")))
    api.include_model(model)
    if db_mode == "async":
        await api.initialize()
    else:
        api.initialize()
    api.mount_jsonrpc()
    api.attach_diagnostics()
    app.include_router(api.router)
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test"), api


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_opspec_deps_execute_in_pre_tx_for_rest_and_rpc(db_mode: str) -> None:
    Base.metadata.clear()
    events: list[str] = []

    def sec_gate() -> None:
        events.append("sec")

    def dep_gate() -> None:
        events.append("dep")

    class Item(Base, GUIDPk):
        __tablename__ = "opspec_pre_tx_item"

        name = Column(String, nullable=False)
        __tigrbl_ops__ = (
            OpSpec(
                alias="create",
                target="create",
                secdeps=(sec_gate,),
                deps=(dep_gate,),
            ),
        )

        @hook_ctx(ops="create", phase="PRE_TX_BEGIN")
        async def pre_tx_begin(cls, ctx):
            events.append("hook")

        @hook_ctx(ops="create", phase="START_TX")
        async def start_tx(cls, ctx):
            events.append("start")

    client, _ = await _build_client(Item, db_mode)

    events.clear()
    rest = await client.post("/item", json={"name": "rest"})
    assert rest.status_code == 201
    rest_payload = rest.json()
    assert isinstance(rest_payload, dict)
    assert rest_payload["name"] == "rest"
    assert events[:4] == ["sec", "dep", "hook", "start"]

    events.clear()
    rpc = await client.post(
        "/rpc",
        json={"id": "1", "method": "Item.create", "params": {"name": "rpc"}},
    )
    assert rpc.status_code == 200
    rpc_payload = rpc.json()["result"]
    assert isinstance(rpc_payload, dict)
    assert rpc_payload["name"] == "rpc"
    assert events[:4] == ["sec", "dep", "hook", "start"]

    await client.aclose()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_opspec_dep_failure_aborts_before_start_tx_for_rest_and_rpc(
    db_mode: str,
) -> None:
    Base.metadata.clear()
    events: list[str] = []

    def sec_gate() -> None:
        events.append("sec")

    def failing_dep() -> None:
        events.append("dep")
        raise RuntimeError("blocked")

    class Item(Base, GUIDPk):
        __tablename__ = "opspec_pre_tx_abort_item"

        name = Column(String, nullable=False)
        __tigrbl_ops__ = (
            OpSpec(
                alias="create",
                target="create",
                secdeps=(sec_gate,),
                deps=(failing_dep,),
            ),
        )

        @hook_ctx(ops="create", phase="START_TX")
        async def start_tx(cls, ctx):
            events.append("start")

    client, _ = await _build_client(Item, db_mode)

    rest = await client.post("/item", json={"name": "rest"})
    assert rest.status_code >= 400
    rest_payload = rest.json()
    assert isinstance(rest_payload, dict)
    assert events == ["sec", "dep"]

    events.clear()
    rpc = await client.post(
        "/rpc",
        json={"id": "1", "method": "Item.create", "params": {"name": "rpc"}},
    )
    assert rpc.status_code == 200
    payload = rpc.json()
    assert isinstance(payload, dict)
    assert "error" in payload and isinstance(payload["error"], dict)
    assert payload["error"]["code"] == -32603
    # Parity: JSON-RPC mapped HTTP status matches REST status and both traces align.
    assert _RPC_TO_HTTP[payload["error"]["code"]] == rest.status_code
    assert events == ["sec", "dep"]

    await client.aclose()
