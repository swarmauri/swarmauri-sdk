"""Lesson 20.2: Mounting favicons on ``TigrblApp``.

This lesson demonstrates app-first mounting with the instance-bound
``mount_favicon`` helper for discoverable bootstrap configuration.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl import TigrblApp


@pytest.mark.asyncio
async def test_app_mount_favicon_default_route() -> None:
    """Mount ``/favicon.ico`` on an app using the convenience helper."""
    app = TigrblApp()

    # A clear, explicit call keeps mount behavior easy to discover.
    app.mount_favicon(name="lesson_app_default_favicon")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/favicon.ico")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")


@pytest.mark.asyncio
async def test_app_mount_favicon_custom_route() -> None:
    """Mount a namespaced favicon route for advanced app layouts."""
    app = TigrblApp()

    app.mount_favicon(path="/assets/favicon.ico", name="lesson_app_assets_favicon")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/assets/favicon.ico")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")
