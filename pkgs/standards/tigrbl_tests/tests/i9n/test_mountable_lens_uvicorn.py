import httpx
import pytest

from tigrbl import TigrblApi, TigrblApp
from tigrbl.system import mount_lens

from .uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_lens_mountable_on_tigrbl_app_uvicorn():
    app = TigrblApp()
    mount_lens(app, path="/custom/lens", name="lens_custom")

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/custom/lens")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert "api-reference" in response.text
    finally:
        await stop_uvicorn_server(server, task)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_lens_mountable_on_tigrbl_api_uvicorn():
    api = TigrblApi()
    mount_lens(api, path="/custom/lens", name="lens_custom")

    base_url, server, task = await run_uvicorn_in_task(api)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/custom/lens")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert "api-reference" in response.text
    finally:
        await stop_uvicorn_server(server, task)
