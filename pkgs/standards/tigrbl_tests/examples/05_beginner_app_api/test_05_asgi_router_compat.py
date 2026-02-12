import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl import TigrblApi, TigrblApp


@pytest.mark.asyncio
async def test_tigrbl_api_serves_asgi_requests():
    """TigrblApi should handle ASGI requests without framework adapters."""
    api = TigrblApi()

    @api.get("/health")
    def health():
        return {"ok": True}

    transport = ASGITransport(app=api)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"ok": True}


@pytest.mark.asyncio
async def test_tigrbl_app_serves_asgi_requests():
    """TigrblApp should handle ASGI requests without framework adapters."""
    app = TigrblApp()

    @app.get("/health")
    def health():
        return {"ok": True}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"ok": True}
