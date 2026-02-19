import httpx
import pytest

from tigrbl import TigrblRouter, TigrblApp
from tigrbl.system import mount_swagger

from .uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_swagger_mountable_on_tigrbl_app_uvicorn():
    app = TigrblApp()
    mount_swagger(app, path="/custom/docs", name="swagger_custom")

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/custom/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert "swagger-ui" in response.text
    finally:
        await stop_uvicorn_server(server, task)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_swagger_mountable_on_tigrbl_api_uvicorn():
    api = TigrblRouter()
    mount_swagger(api, path="/custom/docs", name="swagger_custom")

    base_url, server, task = await run_uvicorn_in_task(api)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/custom/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert "swagger-ui" in response.text
    finally:
        await stop_uvicorn_server(server, task)
