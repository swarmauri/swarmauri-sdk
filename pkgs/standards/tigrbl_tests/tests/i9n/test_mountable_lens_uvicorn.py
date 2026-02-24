import httpx
import pytest

from tigrbl import TigrblRouter, TigrblApp
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
        assert 'id="root"' in response.text
        assert 'type="importmap"' in response.text
        assert (
            '"@tigrbljs/tigrbl-lens": "https://esm.sh/@tigrbljs/tigrbl-lens@latest"'
            in response.text
        )
        assert (
            'href="https://esm.sh/@tigrbljs/tigrbl-lens@latest/dist/tigrbl-lens.css?css"'
            in response.text
        )
        assert 'import { createRoot } from "react-dom/client";' in response.text
    finally:
        await stop_uvicorn_server(server, task)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_lens_mountable_on_tigrbl_api_uvicorn():
    router = TigrblRouter()
    mount_lens(router, path="/custom/lens", name="lens_custom")

    base_url, server, task = await run_uvicorn_in_task(router)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/custom/lens")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert 'id="root"' in response.text
        assert 'url: "/openrpc.json"' in response.text
    finally:
        await stop_uvicorn_server(server, task)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_lens_mountable_with_openrpc_spec_path_uvicorn():
    app = TigrblApp()
    mount_lens(
        app,
        path="/custom/lens",
        name="lens_custom",
        spec_path="/custom/openrpc.json",
    )

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/custom/lens")
        assert response.status_code == 200
        assert 'url: "/custom/openrpc.json"' in response.text
    finally:
        await stop_uvicorn_server(server, task)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_lens_mountable_with_tigrbl_app_method_uvicorn():
    app = TigrblApp()
    app.mount_lens(
        path="/custom/lens", name="lens_custom", spec_path="/custom/openrpc.json"
    )

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/custom/lens")
        assert response.status_code == 200
        assert 'url: "/custom/openrpc.json"' in response.text
    finally:
        await stop_uvicorn_server(server, task)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_lens_mountable_with_tigrbl_api_method_uvicorn():
    router = TigrblRouter()
    router.mount_lens(path="/custom/lens", name="lens_custom")

    base_url, server, task = await run_uvicorn_in_task(router)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/custom/lens")
        assert response.status_code == 200
        assert 'url: "/openrpc.json"' in response.text
    finally:
        await stop_uvicorn_server(server, task)
