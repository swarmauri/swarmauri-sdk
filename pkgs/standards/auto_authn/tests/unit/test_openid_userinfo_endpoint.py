"""Tests for OpenID Connect UserInfo endpoint."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status

from auto_authn.v2.app import app
from auto_authn.v2.fastapi_deps import get_current_principal


@pytest.mark.unit
@pytest.mark.asyncio
async def test_userinfo_requires_access_token(async_client):
    resp = await async_client.get("/userinfo")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.unit
@pytest.mark.asyncio
async def test_userinfo_returns_claims_json(async_client):
    user = MagicMock(
        id=1,
        username="alice",
        email="alice@example.com",
        address="1 Main St",
        phone="123",
    )

    async def override_get_current_principal(*args, **kwargs):
        return user

    app.dependency_overrides[get_current_principal] = override_get_current_principal

    mock_coder = MagicMock()
    mock_coder.async_decode = AsyncMock(
        return_value={"scope": "profile email address phone"}
    )

    headers = {"Authorization": "Bearer token"}
    with patch("auto_authn.v2.oidc_userinfo.JWTCoder.default", return_value=mock_coder):
        resp = await async_client.get("/userinfo", headers=headers)

    app.dependency_overrides.pop(get_current_principal, None)

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == {
        "sub": "1",
        "name": "alice",
        "email": "alice@example.com",
        "address": "1 Main St",
        "phone_number": "123",
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_userinfo_signed_jwt(async_client):
    user = MagicMock(id=1, username="bob", email="bob@example.com")

    async def override_get_current_principal(*args, **kwargs):
        return user

    app.dependency_overrides[get_current_principal] = override_get_current_principal

    mock_coder = MagicMock()
    mock_coder.async_decode = AsyncMock(return_value={"scope": ""})
    mock_svc = MagicMock()
    mock_svc.mint = AsyncMock(return_value="signed")

    headers = {"Authorization": "Bearer token", "Accept": "application/jwt"}
    with (
        patch("auto_authn.v2.oidc_userinfo.JWTCoder.default", return_value=mock_coder),
        patch("auto_authn.v2.oidc_userinfo._svc", return_value=(mock_svc, "kid1")),
    ):
        resp = await async_client.get("/userinfo", headers=headers)

    app.dependency_overrides.pop(get_current_principal, None)

    assert resp.status_code == status.HTTP_200_OK
    assert resp.headers["content-type"] == "application/jwt"
    assert resp.text == "signed"
    mock_svc.mint.assert_awaited_once()
