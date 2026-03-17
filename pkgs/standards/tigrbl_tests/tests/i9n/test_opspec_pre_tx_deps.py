from __future__ import annotations

import inspect

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, String
from tigrbl import TableBase, TigrblApp
from tigrbl.shortcuts.engine import mem
from tigrbl.decorators.hook import hook_ctx
from tigrbl._spec import OpSpec
from tigrbl.orm.mixins import GUIDPk
from tigrbl.runtime.status import HTTPException


async def _build_client(model: type, db_mode: str) -> tuple[AsyncClient, TigrblApp]:
    app = TigrblApp(engine=mem(async_=(db_mode == "async")))
    app.include_table(model)
    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    router = app.router
    engine = app.engine
    app = TigrblApp(engine=engine)
    app.include_router(router)
    app.mount_jsonrpc()
    app.attach_diagnostics()
    return (
        AsyncClient(transport=ASGITransport(app=app), base_url="http://test"),
        app,
    )


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_opspec_deps_execute_in_pre_tx_for_rest_and_rpc(db_mode: str) -> None:
    TableBase.metadata.clear()
    events: list[str] = []

    def sec_gate_one() -> None:
        events.append("sec:one")

    def sec_gate_two() -> None:
        events.append("sec:two")

    def dep_gate_one() -> None:
        events.append("dep:one")

    def dep_gate_two() -> None:
        events.append("dep:two")

    class Item(TableBase, GUIDPk):
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
    secdep_idx = next(
        i
        for i, step in enumerate(steps)
        if step.startswith("PRE_TX_BEGIN:hook:dep:security:")
    )
    dep_idx = next(
        i
        for i, step in enumerate(steps)
        if step.startswith("PRE_TX_BEGIN:hook:dep:extra:")
    )
    handler_idx = next(i for i, step in enumerate(steps) if step.startswith("HANDLER:"))
    assert secdep_idx < dep_idx < handler_idx

    events.clear()
    rpc = await client.post(
        "/rpc",
        json={"id": "1", "method": "Item.create", "params": {"name": "rpc"}},
    )
    assert rpc.status_code == 200
    assert rpc.json() == {"jsonrpc": "2.0", "result": None, "id": "1"}
    assert events == []

    await client.aclose()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_opspec_dep_failure_aborts_before_start_tx_for_rest_and_rpc(
    db_mode: str,
) -> None:
    TableBase.metadata.clear()
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

    class Item(TableBase, GUIDPk):
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
    assert rpc.json() == {"jsonrpc": "2.0", "result": None, "id": "1"}
    assert events == []

    await client.aclose()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_secdep_auth_failure_and_success_parity_for_rest_and_rpc(
    db_mode: str,
) -> None:
    TableBase.metadata.clear()
    events: list[str] = []

    auth_state = {"allow": False}

    def auth_gate() -> None:
        events.append("sec")
        if not auth_state["allow"]:
            raise HTTPException(status_code=401, detail="Unauthorized")

    class Item(TableBase, GUIDPk):
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
    assert rpc_deny.json() == {"jsonrpc": "2.0", "result": None, "id": "1"}
    assert events == []

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
    assert rpc_allow.json() == {"jsonrpc": "2.0", "result": None, "id": "2"}
    assert events == []

    await client.aclose()
