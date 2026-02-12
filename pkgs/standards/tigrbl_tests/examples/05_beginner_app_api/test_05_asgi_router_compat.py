from httpx import ASGITransport, AsyncClient

from tigrbl import TigrblApi, TigrblApp


async def _get_json(app, path: str):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(path)
    return response


def test_tigrbl_api_is_asgi_compatible():
    """TigrblApi should serve routes as an ASGI app."""
    api = TigrblApi()

    @api.get("/health")
    def health():
        return {"ok": True}

    import asyncio

    response = asyncio.run(_get_json(api, "/health"))

    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_tigrbl_app_is_asgi_compatible():
    """TigrblApp should serve routes as an ASGI app."""
    app = TigrblApp()

    @app.get("/health")
    def health():
        return {"ok": True}

    import asyncio

    response = asyncio.run(_get_json(app, "/health"))

    assert response.status_code == 200
    assert response.json() == {"ok": True}
