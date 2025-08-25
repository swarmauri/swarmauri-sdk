"""Tests for OAuth2 token introspection compliance with RFC 7662."""

import pytest
from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient
from uuid import uuid4

from auto_authn.v2.routers.auth_flows import router
from auto_authn.v2.fastapi_deps import get_async_db
from auto_authn.v2.jwtoken import JWTCoder


# RFC 7662 specification excerpt for reference within tests
RFC7662_SPEC = """
RFC 7662 - OAuth 2.0 Token Introspection

2.1. Introspection Request
   The introspection endpoint MUST handle HTTP POST requests with
   Content-Type application/x-www-form-urlencoded.  The body MUST
   include the "token" parameter.

2.2. Introspection Response
   The introspection endpoint responds with a JSON object that includes
   an "active" boolean value.  If the token is invalid, expired, revoked,
   or otherwise not active, the value of "active" MUST be false.
"""


@pytest.mark.unit
@pytest.mark.asyncio
async def test_introspection_endpoint_returns_active_field(enable_rfc7662):
    """RFC 7662 §2.2: Response must include an 'active' boolean."""
    app = FastAPI()
    app.include_router(router)

    async def override_db():
        yield None

    app.dependency_overrides[get_async_db] = override_db

    jwt_coder = JWTCoder.default()
    sub = uuid4()
    tid = uuid4()
    token = await jwt_coder.async_sign(sub=str(sub), tid=str(tid))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/introspect", data={"token": token})
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body.get("active") is True
    assert body.get("sub") == str(sub)
    assert body.get("tid") == str(tid)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_introspection_requires_token_parameter(enable_rfc7662):
    """RFC 7662 §2.1: Request body MUST include the 'token' parameter."""
    app = FastAPI()
    app.include_router(router)

    async def override_db():
        yield None

    app.dependency_overrides[get_async_db] = override_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/introspect", data={})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
