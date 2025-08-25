"""Tests for missing OAuth2 Client Management endpoints (RFC 7592)."""

import pytest
from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient

from auto_authn.v2.rfc7591 import include_rfc7591
from auto_authn.v2.runtime_cfg import settings


@pytest.mark.unit
@pytest.mark.asyncio
async def test_rfc7592_client_management_not_implemented(monkeypatch) -> None:
    """Attempts to manage clients return 404 as the endpoints are absent."""
    app = FastAPI()
    monkeypatch.setattr(settings, "enable_rfc7591", True)
    include_rfc7591(app)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/clients/some-client-id")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
