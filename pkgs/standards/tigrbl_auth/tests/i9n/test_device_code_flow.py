"""Integration test for Device Code (RFC 8628) flow on the canon tigrbl_auth app."""

import pytest
from fastapi import status
from httpx import AsyncClient

from tigrbl_auth.rfc.rfc8628 import approve_device_code


@pytest.mark.integration
@pytest.mark.asyncio
async def test_device_code_flow(async_client: AsyncClient) -> None:
    """Device code flow should exchange a code for an access token after approval."""
    auth_resp = await async_client.post(
        "/device_codes/device_authorization",
        data={"client_id": "test-client", "scope": "openid"},
    )
    assert auth_resp.status_code == status.HTTP_200_OK
    data = auth_resp.json()
    device_code = data["device_code"]
    assert "user_code" in data

    payload = {
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "device_code": device_code,
        "client_id": "test-client",
    }
    pending = await async_client.post("/token", data=payload)
    assert pending.status_code == status.HTTP_400_BAD_REQUEST
    assert pending.json()["error"] == "authorization_pending"

    await approve_device_code.__wrapped__(
        {"payload": {"id": device_code, "sub": "user", "tid": "tenant"}}
    )
    success = await async_client.post("/token", data=payload)
    assert success.status_code == status.HTTP_200_OK
    token_data = success.json()
    assert "access_token" in token_data
    assert token_data["token_type"].lower() == "bearer"
