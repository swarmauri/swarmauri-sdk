"""Tests for the OpenID Connect UserInfo endpoint."""

import pytest
from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient

from auto_authn.v2.jwtoken import JWTCoder
from auto_authn.v2.routers.auth_flows import router


@pytest.mark.unit
@pytest.mark.asyncio
async def test_openid_userinfo_endpoint() -> None:
    """`/userinfo` returns subject claims when provided a bearer token."""
    app = FastAPI()
    app.include_router(router)
    token = await JWTCoder.default().async_sign(sub="user1", tid="tenant1")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/userinfo", headers={"Authorization": f"Bearer {token}"}
        )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["sub"] == "user1"
