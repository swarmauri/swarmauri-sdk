"""Tests for OAuth 2.0 Device Authorization Grant compliance (RFC 8628).

Relevant excerpts from the specification:

RFC 8628 §3.2 Device Authorization Response:
    The authorization server MUST return a JSON object containing
    ``device_code``, ``user_code``, ``verification_uri``,
    ``verification_uri_complete``, ``expires_in``, and ``interval``.

RFC 8628 §3.4 Access Token Request:
    The client makes a request to the token endpoint using
    ``grant_type=urn:ietf:params:oauth:grant-type:device_code`` and the
    ``device_code`` received in the prior step.

RFC 8628 §3.5 Token Error Response:
    If the user has not yet completed the authorization process the
    server MUST respond with ``error=authorization_pending``.
"""

import pytest
from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient

from auto_authn.v2.routers.auth_flows import router, device_store


@pytest.mark.unit
@pytest.mark.asyncio
async def test_device_authorization_response_fields():
    app = FastAPI()
    app.include_router(router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/device/code", data={"client_id": "abc"})
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    for field in [
        "device_code",
        "user_code",
        "verification_uri",
        "verification_uri_complete",
        "expires_in",
        "interval",
    ]:
        assert field in body


@pytest.mark.unit
@pytest.mark.asyncio
async def test_token_requires_device_code():
    app = FastAPI()
    app.include_router(router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        data = {"grant_type": "urn:ietf:params:oauth:grant-type:device_code"}
        resp = await client.post("/token", data=data)
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = resp.json()["detail"]
    assert detail[0]["loc"][-1] == "device_code"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_token_returns_authorization_pending():
    app = FastAPI()
    app.include_router(router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auth_resp = await client.post("/device/code", data={"client_id": "abc"})
        device_code = auth_resp.json()["device_code"]
        resp = await client.post(
            "/token",
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": device_code,
            },
        )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()["error"] == "authorization_pending"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_token_exchanges_code_when_approved():
    app = FastAPI()
    app.include_router(router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auth_resp = await client.post("/device/code", data={"client_id": "abc"})
        payload = auth_resp.json()
        device_store.approve(payload["user_code"])
        resp = await client.post(
            "/token",
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": payload["device_code"],
            },
        )
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert "access_token" in body and "refresh_token" in body
