"""Lesson 20.1: Mounting favicons from bound ``TigrblApi`` helpers.

This lesson demonstrates direct usage of ``api.mount_favicon(...)`` after
binding the system helper to the API class.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl import TigrblApi, TigrblApp


@pytest.mark.asyncio
async def test_api_mount_favicon_default_route() -> None:
    """Mount SVG favicon route and redirect ``/favicon.ico``."""
    api = TigrblApi()

    # Pedagogical pattern: use the bound helper directly from the API object.
    api.mount_favicon(name="lesson_api_default_favicon")

    app = TigrblApp()
    app.include_router(api.router)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        svg_response = await client.get("/favicon.svg")
        ico_response = await client.get("/favicon.ico", follow_redirects=False)

    assert svg_response.status_code == 200
    assert svg_response.headers["content-type"].startswith("image/svg+xml")
    assert ico_response.status_code == 307
    assert ico_response.headers["location"] == "/favicon.svg"


@pytest.mark.asyncio
async def test_api_mount_favicon_custom_route() -> None:
    """Mount a custom favicon path when branding routes are namespaced."""
    api = TigrblApi()
    api.mount_favicon(path="/brand/favicon.svg", name="lesson_api_brand_favicon")

    app = TigrblApp()
    app.include_router(api.router)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        svg_response = await client.get("/brand/favicon.svg")
        ico_response = await client.get("/favicon.ico", follow_redirects=False)

    assert svg_response.status_code == 200
    assert svg_response.headers["content-type"].startswith("image/svg+xml")
    assert ico_response.status_code == 307
    assert ico_response.headers["location"] == "/brand/favicon.svg"
