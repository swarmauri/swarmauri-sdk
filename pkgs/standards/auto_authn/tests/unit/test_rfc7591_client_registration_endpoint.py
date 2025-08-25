"""Tests for OAuth2 Dynamic Client Registration endpoint (RFC 7591)."""

import pytest
from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient

from auto_authn.v2.routers.auth_flows import router
from auto_authn.v2.runtime_cfg import settings


@pytest.mark.unit
@pytest.mark.asyncio
async def test_rfc7591_client_registration_success(monkeypatch) -> None:
    """Posting RFC 7591 client metadata to `/register` returns client credentials."""
    app = FastAPI()
    app.include_router(router)
    monkeypatch.setattr(settings, "enable_rfc7591", True)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"redirect_uris": ["https://client.example/cb"]}
        resp = await client.post("/register", json=payload)
    assert resp.status_code == status.HTTP_201_CREATED
    body = resp.json()
    assert "client_id" in body and "client_secret" in body
