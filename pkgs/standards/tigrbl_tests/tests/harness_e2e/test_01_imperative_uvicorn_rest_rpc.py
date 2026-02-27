from __future__ import annotations

import inspect

import httpx
import pytest
from tigrbl_client import TigrblClient

from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String

from tigrbl_tests.examples._support import pick_unique_port, start_uvicorn, stop_uvicorn


@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_imperative_to_uvicorn_to_rest_client_e2e() -> None:
    """Imperative app: REST create works end-to-end."""

    class Widget(Base, GUIDPk):
        __tablename__ = "harness_imp_rest"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)

    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    app.attach_diagnostics(prefix="", app=app)

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            r = await client.post(f"/{Widget.__name__.lower()}", json={"name": "alpha"})
            assert r.status_code in {200, 201}
            assert r.json()["name"] == "alpha"
    finally:
        await stop_uvicorn(server, task)


@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_imperative_to_uvicorn_to_rpc_client_e2e() -> None:
    """Imperative app: JSON-RPC create works end-to-end."""

    class Widget(Base, GUIDPk):
        __tablename__ = "harness_imp_rpc"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)

    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    app.mount_jsonrpc(prefix="/rpcx")
    app.attach_diagnostics(prefix="", app=app)

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
async def test_imperative_to_uvicorn_rest_and_rpc_parity_e2e() -> None:
    """Imperative app: REST create is visible via RPC list."""

    class Widget(Base, GUIDPk):
        __tablename__ = "harness_imp_parity"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)

    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    app.mount_jsonrpc(prefix="/rpcx")
    app.attach_diagnostics(prefix="", app=app)

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as http:
            r = await http.post(f"/{Widget.__name__.lower()}", json={"name": "gamma"})
            assert r.status_code in {200, 201}

        rpc = TigrblClient(f"{base_url}/rpcx")
        try:
            rpc_response = await rpc.acall("Widget.list", params={})
            items = (
                rpc_response.get("items")
                if isinstance(rpc_response, dict)
                else rpc_response
            )
            assert items
            assert any(it.get("name") == "gamma" for it in items)
        finally:
            await rpc.aclose()
    finally:
        await stop_uvicorn(server, task)
