"""Tests for OAuth 2.0 token endpoint compliance with RFC 6749 §5.2."""

import pytest
from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient

from auto_authn.v2.routers.auth_flows import router
from auto_authn.v2.runtime_cfg import settings


@pytest.fixture()
def enable_rfc6749():
    original = settings.enable_rfc6749
    settings.enable_rfc6749 = True
    try:
        yield
    finally:
        settings.enable_rfc6749 = original


@pytest.mark.unit
@pytest.mark.asyncio
async def test_missing_grant_type_returns_invalid_request(enable_rfc6749):
    """RFC 6749 §5.2: grant_type is required."""
    app = FastAPI()
    app.include_router(router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        data = {"username": "user", "password": "pass"}
        resp = await client.post("/token", data=data)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()["error"] == "invalid_request"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_unsupported_grant_type_returns_error(enable_rfc6749):
    """RFC 6749 §5.2: unsupported_grant_type is returned for unknown grants."""
    app = FastAPI()
    app.include_router(router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        data = {
            "username": "user",
            "password": "pass",
            "grant_type": "client_credentials",
        }
        resp = await client.post("/token", data=data)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()["error"] == "unsupported_grant_type"


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "data",
    [
        {"grant_type": "password", "username": "user"},
        {"grant_type": "password", "password": "pass"},
    ],
)
async def test_password_grant_requires_username_and_password(data, enable_rfc6749):
    """RFC 6749 §4.3: username and password parameters are required."""
    app = FastAPI()
    app.include_router(router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/token", data=data)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()["error"] == "invalid_request"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_authorization_code_grant_requires_code(enable_rfc6749):
    """RFC 6749 §4.1.3: code and redirect_uri are required."""
    app = FastAPI()
    app.include_router(router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        data = {
            "grant_type": "authorization_code",
            "redirect_uri": "https://c",
            "client_id": "abc",
        }
        resp = await client.post("/token", data=data)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()["error"] == "invalid_request"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_unsupported_grant_type_when_disabled():
    """Without RFC 6749 enforcement FastAPI validation is returned."""
    app = FastAPI()
    app.include_router(router)
    transport = ASGITransport(app=app)
    original = settings.enable_rfc6749
    settings.enable_rfc6749 = False
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            data = {
                "username": "user",
                "password": "pass",
                "grant_type": "client_credentials",
            }
            resp = await client.post("/token", data=data)
    finally:
        settings.enable_rfc6749 = original
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = resp.json()["detail"]
    assert detail[0]["loc"][-1] == "grant_type"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_token_endpoint_requires_client_auth():
    """The token endpoint must reject requests without client authentication."""
    app = FastAPI()
    app.include_router(router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/token", data={"grant_type": "authorization_code"})
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp.json()["error"] == "invalid_client"
