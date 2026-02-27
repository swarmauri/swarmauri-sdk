from __future__ import annotations

import inspect

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, String
from tigrbl import Base, TigrblApp
from tigrbl.shortcuts.engine import mem
from tigrbl.hook import hook_ctx
from tigrbl._spec import OpSpec
from tigrbl.orm.mixins import GUIDPk
from tigrbl.runtime.status import _RPC_TO_HTTP, ERROR_MESSAGES, HTTPException


async def _build_client(model: type, db_mode: str) -> tuple[AsyncClient, TigrblApp]:
    app = TigrblApp(engine=mem(async_=(db_mode == "async")))
    app.include_table(model)
    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    host_app = TigrblApp(engine=app.engine)
    host_app.include_router(app.router)
    host_app.mount_jsonrpc()
    host_app.attach_diagnostics()
    return (
        AsyncClient(transport=ASGITransport(app=host_app), base_url="http://test"),
        app,
    )


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_opspec_deps_execute_in_pre_tx_for_rest_and_rpc(db_mode: str) -> None:
    Base.metadata.clear()
    events: list[str] = []

    def sec_gate_one() -> None:
        events.append("sec:one")

    def sec_gate_two() -> None:
        events.append("sec:two")

    def dep_gate_one() -> None:
        events.append("dep:one")

    def dep_gate_two() -> None:
        events.append("dep:two")

    class Item(Base, GUIDPk):
        __tablename__ = "opspec_pre_tx_item"

        name = Column(String, nullable=False)
        __tigrbl_ops__ = (
            OpSpec(
                alias="create",
                target="create",
                secdeps=(sec_gate_one, sec_gate_two),
                deps=(dep_gate_one, dep_gate_two),
            ),
        )

        @hook_ctx(ops="create", phase="PRE_TX_BEGIN")
        async def pre_tx_begin(cls, ctx):
            events.append("hook")

        @hook_ctx(ops="create", phase="START_TX")
        async def start_tx(cls, ctx):
            events.append("start")

        @hook_ctx(ops="create", phase="HANDLER")
        async def handler(cls, ctx):
            events.append("handler")

    client, _ = await _build_client(Item, db_mode)

    events.clear()
    rest = await client.post("/item", json={"name": "rest"})
    assert rest.status_code == 201
    rest_payload = rest.json()
    assert isinstance(rest_payload, dict)
    assert rest_payload["name"] == "rest"
    assert events == [
        "hook",
        "sec:one",
        "sec:two",
        "dep:one",
        "dep:two",
        "start",
        "handler",
    ]
    assert events.count("sec:one") == 1
    assert events.count("sec:two") == 1
    assert events.count("dep:one") == 1
    assert events.count("dep:two") == 1

    kernelz = (await client.get("/system/kernelz")).json()
    steps = kernelz["Item"]["create"]
    secdep_idx = next(i for i, step in enumerate(steps) if ":secdep" in step)
    dep_idx = next(i for i, step in enumerate(steps) if step.endswith(":dep"))
    handler_idx = next(i for i, step in enumerate(steps) if "HANDLER:" in step)
    assert secdep_idx < dep_idx < handler_idx

    events.clear()
    rpc = await client.post(
        "/rpc",
        json={"id": "1", "method": "Item.create", "params": {"name": "rpc"}},
    )
    assert rpc.status_code == 200
    rpc_payload = rpc.json()["result"]
    assert isinstance(rpc_payload, dict)
    assert rpc_payload["name"] == "rpc"
    assert events == [
        "hook",
        "sec:one",
        "sec:two",
        "dep:one",
        "dep:two",
        "start",
        "handler",
    ]
    assert events.count("sec:one") == 1
    assert events.count("sec:two") == 1
    assert events.count("dep:one") == 1
    assert events.count("dep:two") == 1

    await client.aclose()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_opspec_dep_failure_aborts_before_start_tx_for_rest_and_rpc(
    db_mode: str,
) -> None:
    Base.metadata.clear()
    events: list[str] = []

    def sec_gate_one() -> None:
        events.append("sec:one")

    def sec_gate_two() -> None:
        events.append("sec:two")

    def dep_gate_one() -> None:
        events.append("dep:one")

    def dep_gate_two_failing() -> None:
        events.append("dep:two")
        raise RuntimeError("blocked")

    class Item(Base, GUIDPk):
        __tablename__ = "opspec_pre_tx_abort_item"

        name = Column(String, nullable=False)
        __tigrbl_ops__ = (
            OpSpec(
                alias="create",
                target="create",
                secdeps=(sec_gate_one, sec_gate_two),
                deps=(dep_gate_one, dep_gate_two_failing),
            ),
        )

        @hook_ctx(ops="create", phase="START_TX")
        async def start_tx(cls, ctx):
            events.append("start")

        @hook_ctx(ops="create", phase="HANDLER")
        async def handler(cls, ctx):
            events.append("handler")

    client, _ = await _build_client(Item, db_mode)

    rest = await client.post("/item", json={"name": "rest"})
    assert rest.status_code >= 400
    rest_payload = rest.json()
    assert isinstance(rest_payload, dict)
    assert events == ["sec:one", "sec:two", "dep:one", "dep:two"]

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
    assert events == ["sec:one", "sec:two", "dep:one", "dep:two"]

    await client.aclose()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_secdep_auth_failure_and_success_parity_for_rest_and_rpc(
    db_mode: str,
) -> None:
    Base.metadata.clear()
    events: list[str] = []

    auth_state = {"allow": False}

    def auth_gate() -> None:
        events.append("sec")
        if not auth_state["allow"]:
            raise HTTPException(status_code=401, detail="Unauthorized")

    class Item(Base, GUIDPk):
        __tablename__ = "opspec_pre_tx_auth_parity_item"

        name = Column(String, nullable=False)
        __tigrbl_ops__ = (
            OpSpec(alias="create", target="create", secdeps=(auth_gate,)),
        )

        @hook_ctx(ops="create", phase="START_TX")
        async def start_tx(cls, ctx):
            events.append("start")

        @hook_ctx(ops="create", phase="HANDLER")
        async def handler(cls, ctx):
            events.append("handler")

    client, _ = await _build_client(Item, db_mode)

    # deny parity
    events.clear()
    rest_deny = await client.post("/item", json={"name": "rest-deny"})
    assert rest_deny.status_code == 401
    assert events == ["sec"]

    events.clear()
    rpc_deny = await client.post(
        "/rpc",
        json={"id": "1", "method": "Item.create", "params": {"name": "rpc-deny"}},
    )
    assert rpc_deny.status_code == 200
    rpc_err = rpc_deny.json()["error"]
    assert rpc_err["code"] == -32001
    assert _RPC_TO_HTTP[rpc_err["code"]] == rest_deny.status_code
    assert rpc_err["message"] in {"Unauthorized", ERROR_MESSAGES[-32001]}
    assert events == ["sec"]

    # allow parity + ordering
    auth_state["allow"] = True
    events.clear()
    rest_allow = await client.post("/item", json={"name": "rest-allow"})
    assert rest_allow.status_code == 201
    assert rest_allow.json()["name"] == "rest-allow"
    assert events == ["sec", "start", "handler"]

    events.clear()
    rpc_allow = await client.post(
        "/rpc",
        json={"id": "2", "method": "Item.create", "params": {"name": "rpc-allow"}},
    )
    assert rpc_allow.status_code == 200
    assert rpc_allow.json()["result"]["name"] == "rpc-allow"
    assert events == ["sec", "start", "handler"]
    assert events.index("sec") < events.index("start") < events.index("handler")

    await client.aclose()
