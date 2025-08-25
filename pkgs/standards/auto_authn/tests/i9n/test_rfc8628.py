"""Tests for RFC 8628 (Device Authorization Grant).

RFC 8628 §3.2 requires the device authorization response to include the
fields ``device_code``, ``user_code``, ``verification_uri``,
``verification_uri_complete``, ``expires_in`` and ``interval``.  Section 3.5
specifies that the token endpoint returns ``authorization_pending`` while the
user has not yet authorized the device.
"""

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_device_authorization_endpoint(async_client: AsyncClient) -> None:
    """Server should implement the device authorization endpoint."""
    payload = {"client_id": "test-client", "scope": "openid"}
    response = await async_client.post("/device_authorization", data=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    for field in [
        "device_code",
        "user_code",
        "verification_uri",
        "verification_uri_complete",
        "expires_in",
        "interval",
    ]:
        assert field in data


@pytest.mark.integration
@pytest.mark.asyncio
async def test_device_token_polling(async_client: AsyncClient) -> None:
    """Token endpoint should poll until the device code is approved."""
    auth_resp = await async_client.post(
        "/device_authorization", data={"client_id": "test-client"}
    )
    device_code = auth_resp.json()["device_code"]
    payload = {
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "device_code": device_code,
        "client_id": "test-client",
    }
    pending = await async_client.post("/token", data=payload)
    assert pending.status_code == status.HTTP_400_BAD_REQUEST
    assert pending.json()["error"] == "authorization_pending"

    from auto_authn.v2.routers.auth_flows import approve_device_code

    approve_device_code(device_code, sub="user", tid="tenant")
    success = await async_client.post("/token", data=payload)
    assert success.status_code == status.HTTP_200_OK
    data = success.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
