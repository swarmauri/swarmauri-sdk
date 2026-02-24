import httpx
import pytest
from sqlalchemy import Column, String

from tigrbl import Base, TigrblRouter, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.system import mount_openrpc

from .uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server


class Thing(Base, GUIDPk):
    __tablename__ = "things_openrpc_mountable"
    name = Column(String, nullable=False)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_openrpc_mountable_on_tigrbl_app_uvicorn():
    app = TigrblApp(engine=mem(async_=False))
    app.include_model(Thing)
    app.initialize()
    app.mount_jsonrpc(prefix="/rpc")
    mount_openrpc(app, path="/custom/openrpc.json", name="openrpc_custom")

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/custom/openrpc.json")
        assert response.status_code == 200
        payload = response.json()
        assert payload["openrpc"] == "1.2.6"
        assert "methods" in payload
    finally:
        await stop_uvicorn_server(server, task)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_openrpc_mountable_on_tigrbl_api_uvicorn():
    router = TigrblRouter(engine=mem(async_=False), models=[Thing])
    router.initialize()
    router.mount_jsonrpc(prefix="/rpc")
    mount_openrpc(router, path="/custom/openrpc.json", name="openrpc_custom")

    base_url, server, task = await run_uvicorn_in_task(router)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/custom/openrpc.json")
        assert response.status_code == 200
        payload = response.json()
        assert payload["openrpc"] == "1.2.6"
        assert "methods" in payload
    finally:
        await stop_uvicorn_server(server, task)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_openrpc_mountable_with_tigrbl_app_method_uvicorn():
    app = TigrblApp(engine=mem(async_=False))
    app.include_model(Thing)
    app.initialize()
    app.mount_jsonrpc(prefix="/rpc")
    app.mount_openrpc(path="/custom/openrpc.json", name="openrpc_custom")

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/custom/openrpc.json")
        assert response.status_code == 200
        assert response.json()["openrpc"] == "1.2.6"
    finally:
        await stop_uvicorn_server(server, task)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_openrpc_mountable_with_tigrbl_api_method_uvicorn():
    router = TigrblRouter(engine=mem(async_=False), models=[Thing])
    router.initialize()
    router.mount_jsonrpc(prefix="/rpc")
    router.mount_openrpc(path="/custom/openrpc.json", name="openrpc_custom")

    base_url, server, task = await run_uvicorn_in_task(router)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/custom/openrpc.json")
        assert response.status_code == 200
        assert response.json()["openrpc"] == "1.2.6"
    finally:
        await stop_uvicorn_server(server, task)
