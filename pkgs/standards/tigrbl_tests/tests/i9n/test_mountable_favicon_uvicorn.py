import httpx
import pytest

from tigrbl import TigrblApi, TigrblApp
from tigrbl.system import mount_favicon

from .uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_favicon_mountable_on_tigrbl_app_uvicorn():
    app = TigrblApp()
    mount_favicon(app, path="/custom/favicon.ico", name="favicon_custom")

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/custom/favicon.ico")
        assert response.status_code == 200
        assert response.headers.get("content-type") == "image/svg+xml"
        assert response.content
    finally:
        await stop_uvicorn_server(server, task)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_favicon_mountable_on_tigrbl_api_uvicorn():
    api = TigrblApi()
    mount_favicon(api, path="/custom/favicon.ico", name="favicon_custom")

    base_url, server, task = await run_uvicorn_in_task(api)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/custom/favicon.ico")
        assert response.status_code == 200
        assert response.headers.get("content-type") == "image/svg+xml"
        assert response.content
    finally:
        await stop_uvicorn_server(server, task)
