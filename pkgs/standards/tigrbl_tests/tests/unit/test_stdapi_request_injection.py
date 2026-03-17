from __future__ import annotations

from httpx import ASGITransport, AsyncClient

import pytest


from tigrbl import TigrblApp, TigrblRouter
from tigrbl import Request


@pytest.mark.asyncio()
async def test_handler_with_req_name_and_forward_ref_request_annotation() -> None:
    app = TigrblApp(include_docs=True)
    router = TigrblRouter()

    @router.get("/ping")
    def ping(req: "Request") -> dict[str, str]:
        assert isinstance(req, Request)
        return {"path": req.path}

    app.include_router(router)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        ping_response = await client.get("/ping")
        openapi_response = await client.get("/openapi.json")

    assert ping_response.status_code == 500
    assert "AssertionError" in ping_response.json()["detail"]
    assert openapi_response.status_code == 200
