"""Tests for OAuth2 Dynamic Client Registration endpoint (RFC 7591)."""

import pytest
from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient

from auto_authn.rfc7591 import include_rfc7591
from auto_authn.runtime_cfg import settings


@pytest.mark.unit
@pytest.mark.asyncio
async def test_rfc7591_client_registration_endpoint(monkeypatch) -> None:
    """Posting RFC 7591 client metadata to `/register` registers the client."""
    app = FastAPI()
    monkeypatch.setattr(settings, "enable_rfc7591", True)
    include_rfc7591(app)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"redirect_uris": ["https://client.example/cb"]}
        resp = await client.post("/register", json=payload)
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert data["redirect_uris"] == payload["redirect_uris"]
    assert "client_id" in data and "client_secret" in data
    assert data["grant_types"] == ["authorization_code"]
    assert data["response_types"] == ["code"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_rfc7591_client_registration_disabled(monkeypatch) -> None:
    """When disabled, the registration endpoint is unavailable."""
    app = FastAPI()
    monkeypatch.setattr(settings, "enable_rfc7591", False)
    include_rfc7591(app)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"redirect_uris": ["https://client.example/cb"]}
        resp = await client.post("/register", json=payload)
    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.unit
@pytest.mark.asyncio
async def test_rfc7591_redirect_uris_must_use_https(monkeypatch) -> None:
    """Non-HTTPS redirect URIs for non-localhost are rejected."""
    app = FastAPI()
    monkeypatch.setattr(settings, "enable_rfc7591", True)
    include_rfc7591(app)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"redirect_uris": ["http://evil.example/cb"]}
        resp = await client.post("/register", json=payload)
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
