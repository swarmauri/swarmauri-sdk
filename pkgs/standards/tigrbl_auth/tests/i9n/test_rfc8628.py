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
    response = await async_client.post(
        "/device_codes/device_authorization", data=payload
    )
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
async def test_device_token_polling(async_client: AsyncClient, db_session) -> None:
    """Token endpoint should poll until the device code is approved."""
    auth_resp = await async_client.post(
        "/device_codes/device_authorization", data={"client_id": "test-client"}
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

    from tigrbl_auth.rfc.rfc8628 import approve_device_code

    await approve_device_code(device_code, sub="user", tid="tenant", db=db_session)
    success = await async_client.post("/token", data=payload)
    assert success.status_code == status.HTTP_200_OK
    data = success.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_device_code_flow_disabled(async_client: AsyncClient) -> None:
    """Disabling RFC 8628 should remove the device code grant."""
    from tigrbl_auth.runtime_cfg import settings
    from tigrbl_auth.routers import shared

    original = settings.enable_rfc8628
    settings.enable_rfc8628 = False
    shared._ALLOWED_GRANT_TYPES.discard("urn:ietf:params:oauth:grant-type:device_code")
    try:
        resp = await async_client.post(
            "/device_codes/device_authorization",
            data={"client_id": "test-client"},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

        payload = {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": "missing",
            "client_id": "test-client",
        }
        token_resp = await async_client.post("/token", data=payload)
        assert token_resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert token_resp.json()["error"] == "invalid_client"
    finally:
        settings.enable_rfc8628 = original
        if original:
            shared._ALLOWED_GRANT_TYPES.add(
                "urn:ietf:params:oauth:grant-type:device_code"
            )
