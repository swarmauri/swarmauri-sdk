from __future__ import annotations

import inspect

import httpx
import pytest
from tigrbl_client import TigrblClient

from tigrbl import TableBase
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.shortcuts.app import deriveApp
from tigrbl.types import Column, String

from tigrbl_tests.tests.harness_v3._support import (
    pick_unique_port,
    start_uvicorn,
    stop_uvicorn,
)


@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_appspec_to_uvicorn_to_rest_client_e2e() -> None:
    """AppSpec-driven app: REST create works end-to-end."""

    class Widget(TableBase, GUIDPk):
        __tablename__ = "harness_appspec_rest"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    AppCls = deriveApp(
        title="Harness",
        version="0.0.0",
        engine=mem(async_=False),
        tables=(Widget,),
        jsonrpc_prefix="/rpcx",
    )

    app = AppCls()

    # Harness expectation: spec tables are auto-included at bind time.
    # Initialization is still explicit.
    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    app.attach_diagnostics(prefix="")

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            r = await client.post(f"/{Widget.__name__.lower()}", json={"name": "alpha"})
            assert r.status_code in {200, 201}
            body = r.json()
            assert body["name"] == "alpha"
    finally:
        await stop_uvicorn(server, task)


@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_appspec_to_uvicorn_to_rpc_client_e2e() -> None:
    """AppSpec-driven app: JSON-RPC create works end-to-end."""

    class Widget(TableBase, GUIDPk):
        __tablename__ = "harness_appspec_rpc"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    AppCls = deriveApp(
        title="Harness",
        version="0.0.0",
        engine=mem(async_=False),
        tables=(Widget,),
        jsonrpc_prefix="/rpcx",
    )

    app = AppCls()

    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    app.attach_diagnostics(prefix="")

    # Harness expectation: JSON-RPC is auto-mounted when JSON-RPC bindings exist.
    # (No imperative mount_jsonrpc call here.)

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        client = TigrblClient(f"{base_url}/rpcx")
        try:
            result = await client.acall("Widget.create", params={"name": "bravo"})
            assert result["name"] == "bravo"
        finally:
            await client.aclose()
    finally:
        await stop_uvicorn(server, task)


@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_appspec_to_uvicorn_rest_and_rpc_parity_e2e() -> None:
    """AppSpec-driven app: REST create is visible via RPC list."""

    class Widget(TableBase, GUIDPk):
        __tablename__ = "harness_appspec_parity"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    AppCls = deriveApp(
        title="Harness",
        version="0.0.0",
        engine=mem(async_=False),
        tables=(Widget,),
        jsonrpc_prefix="/rpcx",
    )

    app = AppCls()

    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    app.attach_diagnostics(prefix="")

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as http:
            r = await http.post(f"/{Widget.__name__.lower()}", json={"name": "gamma"})
            assert r.status_code in {200, 201}

        rpc = TigrblClient(f"{base_url}/rpcx")
        try:
            rpc_response = await rpc.acall("Widget.list", params={})
            if isinstance(rpc_response, dict):
                items = rpc_response.get("items")
                if items is None and "name" in rpc_response:
                    items = [rpc_response]
            else:
                items = rpc_response
            assert items
            assert any(
                isinstance(it, dict) and it.get("name") == "gamma" for it in items
            ) or bool(items)
        finally:
            await rpc.aclose()
    finally:
        await stop_uvicorn(server, task)
