"""Tests for upcoming RFC 8628 (Device Authorization Grant) support.

These tests describe the expected behaviour for RFC 8628 compliance and are
marked as xfail until the feature is implemented.
"""

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.xfail(reason="Device Authorization Grant (RFC 8628) support planned")
async def test_device_authorization_endpoint(async_client: AsyncClient) -> None:
    """Server should implement the device authorization endpoint."""
    payload = {"client_id": "test-client", "scope": "openid"}
    response = await async_client.post("/device_authorization", data=payload)

    # Expected behaviour once implemented
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "device_code" in data
    assert "user_code" in data
    assert "verification_uri" in data
    assert "verification_uri_complete" in data
    assert "expires_in" in data
    assert "interval" in data


@pytest.mark.integration
@pytest.mark.xfail(reason="Device Authorization Grant (RFC 8628) support planned")
async def test_device_token_exchange(async_client: AsyncClient) -> None:
    """Server should allow exchanging a device code for tokens."""
    payload = {
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "device_code": "dummy",
        "client_id": "test-client",
    }
    response = await async_client.post("/token", data=payload)

    # Expected behaviour once implemented
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
