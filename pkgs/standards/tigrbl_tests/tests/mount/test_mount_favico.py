"""Focused mount tests for bound ``mount_favicon`` helpers.

These tests verify ``TigrblApp`` exposes the system mount method directly,
with SVG redirect and ICO file fallback behavior intact.
"""

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl import TigrblRouter, TigrblApp


class TestMountFaviconOnTigrblApp:
    """Validate favicon mounting behavior for ``TigrblApp`` instances."""

    @pytest.mark.asyncio
    async def test_mount_favicon_svg_route_and_ico_redirect(self) -> None:
        """The default mount serves ``/favicon.svg`` and redirects ``/favicon.ico``."""
        app = TigrblApp()
        app.mount_favicon(name="favicon_default_route")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            svg_response = await client.get("/favicon.svg")
            ico_response = await client.get("/favicon.ico", follow_redirects=False)

        assert svg_response.status_code == 200
        assert svg_response.headers["content-type"].startswith("image/svg+xml")
        assert svg_response.content

        assert ico_response.status_code == 307
        assert ico_response.headers["location"] == "/favicon.svg"

    @pytest.mark.asyncio
    async def test_mount_favicon_supports_custom_svg_path(self) -> None:
        """A custom SVG mount path should be the target for ICO redirects."""
        app = TigrblApp()
        app.mount_favicon(path="/assets/favicon.svg", name="favicon_assets_route")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            svg_response = await client.get("/assets/favicon.svg")
            ico_response = await client.get("/favicon.ico", follow_redirects=False)

        assert svg_response.status_code == 200
        assert svg_response.headers["content-type"].startswith("image/svg+xml")

        assert ico_response.status_code == 307
        assert ico_response.headers["location"] == "/assets/favicon.svg"

    @pytest.mark.asyncio
    async def test_mount_favicon_serves_ico_file_directly(self, tmp_path: Path) -> None:
        """When an ICO file is configured, only ICO should be served directly."""
        app = TigrblApp()
        favicon_ico = tmp_path / "favicon.ico"
        favicon_ico.write_bytes(b"\x00\x00\x01\x00")

        app.mount_favicon(favicon_path=favicon_ico, name="favicon_ico_route")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            ico_response = await client.get("/favicon.ico")
            svg_response = await client.get("/favicon.svg")

        assert ico_response.status_code == 200
        assert ico_response.headers["content-type"].startswith("image/x-icon")
        assert ico_response.content == b"\x00\x00\x01\x00"

        assert svg_response.status_code == 404


class TestMountFaviconOnTigrblRouter:
    """Validate ``TigrblRouter`` no longer exposes favicon mounting."""

    def test_tigrbl_router_does_not_bind_mount_favicon_method(self) -> None:
        """Routers should not expose ``mount_favicon`` directly."""
        router = TigrblRouter()

        assert not hasattr(router, "mount_favicon")
