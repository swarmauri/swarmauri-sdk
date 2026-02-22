import httpx
import pytest

from tigrbl import TigrblRouter, TigrblApp
from tigrbl.system import mount_favicon

from .uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_favicon_mountable_on_tigrbl_app_uvicorn():
    app = TigrblApp()
    mount_favicon(app, path="/custom/favicon.svg", name="favicon_custom")

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        async with httpx.AsyncClient() as client:
            svg_response = await client.get(f"{base_url}/custom/favicon.svg")
            ico_response = await client.get(
                f"{base_url}/favicon.ico", follow_redirects=False
            )
        assert svg_response.status_code == 200
        assert svg_response.headers.get("content-type") == "image/svg+xml"
        assert svg_response.content
        assert ico_response.status_code == 307
        assert ico_response.headers.get("location") == "/custom/favicon.svg"
    finally:
        await stop_uvicorn_server(server, task)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_favicon_mountable_on_tigrbl_api_uvicorn():
    router = TigrblRouter()
    mount_favicon(router, path="/custom/favicon.svg", name="favicon_custom")

    base_url, server, task = await run_uvicorn_in_task(router)
    try:
        async with httpx.AsyncClient() as client:
            svg_response = await client.get(f"{base_url}/custom/favicon.svg")
            ico_response = await client.get(
                f"{base_url}/favicon.ico", follow_redirects=False
            )
        assert svg_response.status_code == 200
        assert svg_response.headers.get("content-type") == "image/svg+xml"
        assert svg_response.content
        assert ico_response.status_code == 307
        assert ico_response.headers.get("location") == "/custom/favicon.svg"
    finally:
        await stop_uvicorn_server(server, task)
