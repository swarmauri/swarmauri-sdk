from __future__ import annotations

from httpx import ASGITransport, AsyncClient

import pytest

from tigrbl.types import APIRouter, Request


@pytest.mark.asyncio()
async def test_handler_with_req_name_and_forward_ref_request_annotation() -> None:
    app = APIRouter(include_docs=True)

    @app.get("/ping")
    def ping(req: "Request") -> dict[str, str]:
        assert isinstance(req, Request)
        return {"path": req.path}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        ping_response = await client.get("/ping")
        openapi_response = await client.get("/openapi.json")

    assert ping_response.status_code == 200
    assert ping_response.json() == {"path": "/ping"}
    assert openapi_response.status_code == 200
