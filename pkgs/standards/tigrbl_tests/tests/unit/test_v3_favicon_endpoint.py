import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl import TigrblApp


@pytest.mark.asyncio
async def test_favicon_endpoint_serves_default_svg_and_redirects_ico():
    app = TigrblApp()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        svg_res = await client.get("/favicon.svg")
        ico_res = await client.get("/favicon.ico", follow_redirects=False)

    assert svg_res.status_code == 200
    assert svg_res.headers.get("content-type") == "image/svg+xml"
    assert svg_res.content

    assert ico_res.status_code == 307
    assert ico_res.headers.get("location") == "/favicon.svg"
