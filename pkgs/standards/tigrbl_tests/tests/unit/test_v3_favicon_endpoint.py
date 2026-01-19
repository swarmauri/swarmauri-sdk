import pytest
from tigrbl.types import App
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_favicon_endpoint_serves_default_icon():
    app = App()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.get("/favicon.ico")

    assert res.status_code == 200
    assert res.headers.get("content-type") == "image/svg+xml"
    assert res.content  # file has some content
