"""Tests for RFC 7662 token introspection compliance."""

import pytest
from httpx import AsyncClient


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


@pytest.mark.integration
@pytest.mark.asyncio
async def test_introspect_valid_api_key(
    async_client: AsyncClient, test_api_key, enable_rfc7662
):
    """Valid API key should yield an active introspection response."""
    response = await async_client.post(
        "/introspect", data={"token": test_api_key._test_raw_key}
    )
    assert response.status_code == 200
    body = response.json()
    assert body.get("active") is True


@pytest.mark.integration
@pytest.mark.asyncio
async def test_introspect_invalid_api_key(async_client: AsyncClient, enable_rfc7662):
    """Invalid API key should yield inactive response per RFC 7662."""
    response = await async_client.post("/introspect", data={"token": "does-not-exist"})
    assert response.status_code == 200
    body = response.json()
    assert body.get("active") is False
