"""Tests for OAuth 2.0 Pushed Authorization Requests compliance with RFC 9126."""

import pytest
from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient

from tigrbl_auth.rfc9126 import DEFAULT_PAR_EXPIRY, router
from tigrbl_auth.fastapi_deps import get_db

# RFC 9126 specification excerpt for reference within tests
RFC9126_SPEC = """
RFC 9126 - OAuth 2.0 Pushed Authorization Requests

3.1. Pushed Authorization Request Endpoint
   Successful responses MUST include a "request_uri" and "expires_in" value
   and use HTTP status code 201 (Created).
"""


@pytest.mark.unit
@pytest.mark.asyncio
async def test_par_returns_request_uri_and_expires(enable_rfc9126, monkeypatch):
    """RFC 9126 §3.1: Response includes request_uri and expires_in."""
    app = FastAPI()
    app.include_router(router)

    async def override_db():
        yield None

    app.dependency_overrides[get_db] = override_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/par", data={"client_id": "abc", "response_type": "code"}
        )
    assert resp.status_code == status.HTTP_201_CREATED
    body = resp.json()
    assert "request_uri" in body
    assert body["expires_in"] == DEFAULT_PAR_EXPIRY


@pytest.mark.unit
@pytest.mark.asyncio
async def test_par_disabled_returns_404(monkeypatch):
    """RFC 9126 §3.1: Endpoint returns 404 when PAR is disabled."""
    from tigrbl_auth.runtime_cfg import settings

    app = FastAPI()
    app.include_router(router)

    async def override_db():
        yield None

    app.dependency_overrides[get_db] = override_db

    original = settings.enable_rfc9126
    settings.enable_rfc9126 = False
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/par", data={})
        assert resp.status_code == status.HTTP_404_NOT_FOUND
    finally:
        settings.enable_rfc9126 = original
