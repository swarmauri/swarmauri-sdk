"""TDD harness: AppSpec -> uvicorn -> REST + JSON-RPC E2E.

This is the highest-level harness:
  AppSpec -> TigrblApp.from_spec(spec)
  -> uvicorn
  -> httpx REST create
  -> httpx JSON-RPC create

It verifies the framework can be driven entirely from spec compilation.
"""

from __future__ import annotations

import httpx
import pytest

from tigrbl_tests.tests.i9n.uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server


@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_appspec_to_uvicorn_rest_and_rpc_roundtrip() -> None:
    from sqlalchemy import Column, String

    from tigrbl import Base
    from tigrbl.app import AppSpec
    from tigrbl.concrete.tigrbl_app import TigrblApp
    from tigrbl.engine.shortcuts import mem
    from tigrbl.orm.mixins import GUIDPk
    from tigrbl.op import OpSpec
    from tigrbl.specs.binding_spec import HttpJsonRpcBindingSpec, HttpRestBindingSpec

    class Widget(Base, GUIDPk):
        __tablename__ = "widgets_appspec_e2e"
        __resource__ = "widget"
        name = Column(String, nullable=False)

    # Declare the op surface explicitly so this test is independent of decorator discovery.
    Widget.__tigrbl_ops__ = (
        OpSpec(
            alias="create",
            target="create",
            bindings=(
                HttpRestBindingSpec(proto="http.rest", path="/widget", methods=("POST",)),
                HttpJsonRpcBindingSpec(proto="http.jsonrpc", rpc_method="Widget.create"),
            ),
        ),
    )

    spec = AppSpec(
        title="Harness",
        version="0.0.0",
        engine=mem(async_=False),
        tables=(Widget,),
        jsonrpc_prefix="/rpcx",
        system_prefix="/system",
    )

    app = TigrblApp.from_spec(spec)

    # Contract: the app is runnable with uvicorn and does not require additional imperative calls.
    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        async with httpx.AsyncClient() as client:
            rest = await client.post(f"{base_url}/widget", json={"name": "alpha"})
            rpc_payload = {
                "jsonrpc": "2.0",
                "method": "Widget.create",
                "params": {"name": "beta"},
                "id": 1,
            }
            rpc = await client.post(f"{base_url}/rpcx/", json=rpc_payload)

        assert rest.status_code == 201
        assert rpc.status_code == 200
        body = rpc.json()
        assert body["result"]["name"] == "beta"
    finally:
        await stop_uvicorn_server(server, task)
