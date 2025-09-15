"""Integration test for token exchange flow on the canon tigrbl_auth app."""

import time

import pytest
from httpx import AsyncClient

from tigrbl_auth.rfc.rfc7519 import encode_jwt, decode_jwt
from tigrbl_auth.rfc.rfc8693 import TOKEN_EXCHANGE_GRANT_TYPE, TokenType


@pytest.mark.integration
@pytest.mark.asyncio
async def test_token_exchange_flow(async_client: AsyncClient, enable_rfc8693) -> None:
    """Server should issue a new access token with requested scope."""
    subject_token = encode_jwt(
        sub="user123", tid="tenant-1", scope="read write", exp=int(time.time()) + 3600
    )
    payload = {
        "grant_type": TOKEN_EXCHANGE_GRANT_TYPE,
        "subject_token": subject_token,
        "subject_token_type": TokenType.ACCESS_TOKEN.value,
        "audience": "https://api.example.com",
        "scope": "read",
    }
    response = await async_client.post("/token/exchange", data=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"].lower() == "bearer"
    claims = decode_jwt(data["access_token"])
    assert claims["sub"] == "user123"
    assert claims["tid"] == "tenant-1"
    assert claims["scopes"] == ["read"]
