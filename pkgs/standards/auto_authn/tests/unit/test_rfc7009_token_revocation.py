"""Tests for OAuth 2.0 Token Revocation compliance with RFC 7009."""

import pytest
from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient

from auto_authn.v2.routers.auth_flows import router
from auto_authn.v2.fastapi_deps import get_async_db
from auto_authn.v2.rfc7009 import is_revoked

# RFC 7009 specification excerpt for reference within tests
RFC7009_SPEC = """
RFC 7009 - OAuth 2.0 Token Revocation

2.2. Revocation Response
   The authorization server responds with HTTP status code 200
   in all cases, even if the token is invalid.
"""


@pytest.mark.unit
@pytest.mark.asyncio
async def test_revoke_returns_200_and_marks_token_revoked(enable_rfc7009, monkeypatch):
    """RFC 7009 §2.2: Revocation returns HTTP 200 and token becomes invalid."""
    app = FastAPI()
    app.include_router(router)

    async def override_db():
        yield None

    app.dependency_overrides[get_async_db] = override_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/revoke", data={"token": "abc"})
    assert resp.status_code == status.HTTP_200_OK
    assert is_revoked("abc")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_revoke_returns_200_for_unknown_token(enable_rfc7009):
    """RFC 7009 §2.2: Endpoint must return HTTP 200 even for unknown tokens."""
    app = FastAPI()
    app.include_router(router)

    async def override_db():
        yield None

    app.dependency_overrides[get_async_db] = override_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/revoke", data={"token": "nonexistent"})
    assert resp.status_code == status.HTTP_200_OK
