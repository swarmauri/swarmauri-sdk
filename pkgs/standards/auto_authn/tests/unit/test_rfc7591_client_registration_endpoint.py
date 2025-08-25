"""Tests for missing OAuth2 Dynamic Client Registration endpoint (RFC 7591)."""

import pytest
from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient

from auto_authn.v2.routers.auth_flows import router


@pytest.mark.unit
@pytest.mark.asyncio
async def test_rfc7591_client_registration_not_implemented() -> None:
    """Posting RFC 7591 client metadata to `/register` yields validation error."""
    app = FastAPI()
    app.include_router(router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"redirect_uris": ["https://client.example/cb"]}
        resp = await client.post("/register", json=payload)
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
