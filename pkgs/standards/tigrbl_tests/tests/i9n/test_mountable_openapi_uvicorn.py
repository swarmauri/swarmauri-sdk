import httpx
import pytest

from tigrbl import TigrblRouter, TigrblApp
from tigrbl.system import mount_openapi

from .uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_openapi_mountable_on_tigrbl_app_uvicorn():
    app = TigrblApp()
    mount_openapi(app, path="/custom/openapi.json", name="openapi_custom")

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/custom/openapi.json")
        assert response.status_code == 200
        payload = response.json()
        assert payload["openapi"] == "3.1.0"
    finally:
        await stop_uvicorn_server(server, task)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_openapi_mountable_on_tigrbl_api_uvicorn():
    router = TigrblRouter()
    mount_openapi(router, path="/custom/openapi.json", name="openapi_custom")

    base_url, server, task = await run_uvicorn_in_task(router)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/custom/openapi.json")
        assert response.status_code == 200
        payload = response.json()
        assert payload["openapi"] == "3.1.0"
    finally:
        await stop_uvicorn_server(server, task)
