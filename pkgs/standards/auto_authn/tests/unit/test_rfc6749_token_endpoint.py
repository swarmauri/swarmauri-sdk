"""Tests for OAuth2 password grant compliance with RFC 6749."""

import pytest
from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient

from auto_authn.v2.routers.auth_flows import router


@pytest.mark.unit
@pytest.mark.asyncio
async def test_token_rejects_unsupported_grant_type():
    """RFC 6749 §4.3: grant_type must be "password"."""
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
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = resp.json()["detail"]
    assert detail[0]["loc"][-1] == "grant_type"


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "data,missing",
    [
        ({"grant_type": "password", "username": "user"}, "password"),
        ({"grant_type": "password", "password": "pass"}, "username"),
    ],
)
async def test_token_requires_username_and_password(data, missing):
    """RFC 6749 §4.3: username and password parameters are required."""
    app = FastAPI()
    app.include_router(router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/token", data=data)
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    fields = {err["loc"][-1] for err in resp.json()["detail"]}
    assert missing in fields
