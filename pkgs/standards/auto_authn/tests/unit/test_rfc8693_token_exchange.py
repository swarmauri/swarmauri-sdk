"""Tests for OAuth 2.0 Token Exchange compliance with RFC 8693."""

import pytest
from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient

from auto_authn.v2.rfc8693 import router
from auto_authn.v2.runtime_cfg import settings

# RFC 8693 specification excerpt for reference within tests
RFC8693_SPEC = """
RFC 8693 - OAuth 2.0 Token Exchange

2.1.  Successful Response
   The authorization server responds with HTTP status code 200 and a
   JSON object containing an issued token.
"""


@pytest.mark.unit
@pytest.mark.asyncio
async def test_token_exchange_returns_access_token(enable_rfc8693):
    """RFC 8693 §2.1: Successful token exchange returns a token."""
    app = FastAPI()
    app.include_router(router)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/token/exchange",
            data={
                "subject_token": "old",
                "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
            },
        )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["access_token"] == "exchanged-old"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_token_exchange_returns_404_when_disabled(monkeypatch):
    """RFC 8693: Endpoint is unavailable when support is disabled."""
    app = FastAPI()
    app.include_router(router)

    monkeypatch.setattr(settings, "enable_rfc8693", False)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/token/exchange",
            data={
                "subject_token": "old",
                "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
            },
        )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
