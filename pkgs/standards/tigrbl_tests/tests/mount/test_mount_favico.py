"""Focused mount tests for bound ``mount_favicon`` helpers.

These tests verify both ``TigrblApp`` and ``TigrblApi`` expose the system
mount method directly, with default fallback behavior intact.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl import TigrblApi, TigrblApp


class TestMountFaviconOnTigrblApp:
    """Validate favicon mounting behavior for ``TigrblApp`` instances."""

    @pytest.mark.asyncio
    async def test_mount_favicon_exposes_default_favicon_route(self) -> None:
        """The default ``/favicon.ico`` route should return SVG content."""
        app = TigrblApp()
        app.mount_favicon(name="favicon_default_route")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/favicon.ico")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("image/svg+xml")
        assert response.content

    @pytest.mark.asyncio
    async def test_mount_favicon_supports_custom_path(self) -> None:
        """A custom mount path should serve the configured favicon endpoint."""
        app = TigrblApp()
        app.mount_favicon(path="/assets/favicon.ico", name="favicon_assets_route")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/assets/favicon.ico")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("image/svg+xml")


class TestMountFaviconOnTigrblApi:
    """Validate favicon mounting behavior for ``TigrblApi`` instances."""

    def test_tigrbl_api_binds_mount_favicon_method(self) -> None:
        """``TigrblApi`` should expose ``mount_favicon`` as an instance API."""
        api = TigrblApi()

        assert hasattr(api, "mount_favicon")

    @pytest.mark.asyncio
    async def test_bound_mount_favicon_supports_api_instances(self) -> None:
        """The bound method should mount favicon routes on APIs."""
        api = TigrblApi()
        api.mount_favicon(path="/branding/favicon.ico", name="api_branding_favicon")

        transport = ASGITransport(app=api)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/branding/favicon.ico")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("image/svg+xml")

    @pytest.mark.asyncio
    async def test_bound_mount_favicon_retains_default_fallback(self) -> None:
        """Passing ``None`` for favicon path should use the default asset."""
        api = TigrblApi()
        api.mount_favicon(path="/fallback/favicon.ico", favicon_path=None)

        transport = ASGITransport(app=api)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/fallback/favicon.ico")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("image/svg+xml")
        assert response.content
