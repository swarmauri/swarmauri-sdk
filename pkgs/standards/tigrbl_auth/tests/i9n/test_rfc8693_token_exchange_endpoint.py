"""Integration tests for RFC 8693 token exchange endpoint.

See RFC 8693: https://www.rfc-editor.org/rfc/rfc8693
"""

import time

import pytest
from fastapi import status
from httpx import AsyncClient

from tigrbl_auth import encode_jwt
from tigrbl_auth.rfc.rfc8693 import TOKEN_EXCHANGE_GRANT_TYPE, TokenType


@pytest.mark.integration
@pytest.mark.asyncio
async def test_token_exchange_endpoint(
    async_client: AsyncClient, enable_rfc8693
) -> None:
    """Server should exchange tokens when RFC 8693 is enabled."""
    subject_token = encode_jwt(sub="user123", exp=int(time.time()) + 3600)
    payload = {
        "grant_type": TOKEN_EXCHANGE_GRANT_TYPE,
        "subject_token": subject_token,
        "subject_token_type": TokenType.ACCESS_TOKEN.value,
    }
    response = await async_client.post("/token/exchange", data=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"].lower() == "bearer"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_token_exchange_endpoint_disabled(async_client: AsyncClient) -> None:
    """Endpoint should return 404 when RFC 8693 is disabled."""
    subject_token = encode_jwt(sub="user123", exp=int(time.time()) + 3600)
    payload = {
        "grant_type": TOKEN_EXCHANGE_GRANT_TYPE,
        "subject_token": subject_token,
        "subject_token_type": TokenType.ACCESS_TOKEN.value,
    }
    response = await async_client.post("/token/exchange", data=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
