from httpx import ASGITransport, AsyncClient

import pytest

from tigrbl import TigrblRouter, TigrblApp


async def _get_json(app, path: str):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(path)
    return response


def test_tigrbl_api_is_asgi_compatible():
    """TigrblRouter should serve routes as an ASGI app."""
    router = TigrblRouter()

    @router.get("/health")
    def health():
        return {"ok": True}

    import asyncio

    response = asyncio.run(_get_json(router, "/health"))

    assert response.status_code == 200
    assert response.json() == {"ok": True}


@pytest.mark.xfail(reason="TigrblApp no longer exposes HTTP verb decorator methods")
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
