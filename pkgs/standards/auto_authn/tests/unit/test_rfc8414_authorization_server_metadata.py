"""Tests for OAuth 2.0 Authorization Server Metadata compliance with RFC 8414."""

import pytest
from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient

from auto_authn.v2.rfc8414 import router
from auto_authn.v2.runtime_cfg import settings

# RFC 8414 specification excerpt for reference within tests
RFC8414_SPEC = """
RFC 8414 - OAuth 2.0 Authorization Server Metadata

3.  Metadata Request
   Authorization server metadata is retrieved from
   the path '/.well-known/oauth-authorization-server'.
"""


@pytest.mark.unit
@pytest.mark.asyncio
async def test_metadata_endpoint_returns_expected_fields(enable_rfc8414):
    """RFC 8414 §3: Metadata endpoint returns required fields."""
    app = FastAPI()
    app.include_router(router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/.well-known/oauth-authorization-server")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    for field in ["issuer", "authorization_endpoint", "token_endpoint", "jwks_uri"]:
        assert field in data


@pytest.mark.unit
@pytest.mark.asyncio
async def test_metadata_scopes_include_standard_scopes(enable_rfc8414):
    """Discovery metadata includes OIDC standard scopes."""
    app = FastAPI()
    app.include_router(router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/.well-known/oauth-authorization-server")
    scopes = resp.json()["scopes_supported"]
    for scope in ["openid", "profile", "email"]:
        assert scope in scopes


@pytest.mark.unit
@pytest.mark.asyncio
async def test_metadata_endpoint_returns_404_when_disabled():
    """RFC 8414 §3: Endpoint may be disabled and should return 404."""
    app = FastAPI()
    app.include_router(router)
    original = settings.enable_rfc8414
    settings.enable_rfc8414 = False
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/.well-known/oauth-authorization-server")
        assert resp.status_code == status.HTTP_404_NOT_FOUND
    finally:
        settings.enable_rfc8414 = original
