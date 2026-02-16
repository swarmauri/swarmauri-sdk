"""Lesson 20.2: Mounting favicons on ``TigrblApp``.

This lesson demonstrates app-first mounting with the instance-bound
``mount_favicon`` helper for discoverable bootstrap configuration.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl import TigrblApp


@pytest.mark.asyncio
async def test_app_mount_favicon_default_route() -> None:
    """Mount SVG favicon route and redirect ``/favicon.ico``."""
    app = TigrblApp()

    # A clear, explicit call keeps mount behavior easy to discover.
    app.mount_favicon(name="lesson_app_default_favicon")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        svg_response = await client.get("/favicon.svg")
        ico_response = await client.get("/favicon.ico", follow_redirects=False)

    assert svg_response.status_code == 200
    assert svg_response.headers["content-type"].startswith("image/svg+xml")
    assert ico_response.status_code == 307
    assert ico_response.headers["location"] == "/favicon.svg"


@pytest.mark.asyncio
async def test_app_mount_favicon_custom_route() -> None:
    """Mount a namespaced favicon route for advanced app layouts."""
    app = TigrblApp()

    app.mount_favicon(path="/assets/favicon.svg", name="lesson_app_assets_favicon")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        svg_response = await client.get("/assets/favicon.svg")
        ico_response = await client.get("/favicon.ico", follow_redirects=False)

    assert svg_response.status_code == 200
    assert svg_response.headers["content-type"].startswith("image/svg+xml")
    assert ico_response.status_code == 307
    assert ico_response.headers["location"] == "/assets/favicon.svg"
