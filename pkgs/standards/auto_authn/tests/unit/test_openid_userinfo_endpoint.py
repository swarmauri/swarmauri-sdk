"""Tests for missing OpenID Connect UserInfo endpoint."""

import pytest
from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient

from auto_authn.v2.routers.auth_flows import router


@pytest.mark.unit
@pytest.mark.asyncio
async def test_openid_userinfo_endpoint_missing() -> None:
    """`/userinfo` should return 404 because the endpoint is not implemented."""
    app = FastAPI()
    app.include_router(router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/userinfo")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
