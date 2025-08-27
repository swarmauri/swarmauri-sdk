"""Tests for OpenID Connect UserInfo endpoint."""

from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status

from auto_authn.v2.app import app
from auto_authn.v2.fastapi_deps import get_current_principal
from auto_authn.v2.db import get_async_db


@pytest.mark.unit
@pytest.mark.asyncio
async def test_userinfo_requires_access_token(async_client):
    resp = await async_client.get("/userinfo")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.unit
@pytest.mark.asyncio
async def test_userinfo_returns_claims_json(async_client):
    @dataclass
    class DummyUser:
        id: str
        tenant_id: str

    user = DummyUser(id="1", tenant_id="1")
    user.username = "alice"
    user.email = "alice@example.com"
    user.address = "1 Main St"
    user.phone = "123"

    async def override_get_current_principal(*args, **kwargs):
        return user

    async def dummy_db():
        yield MagicMock()

    app.dependency_overrides[get_current_principal] = override_get_current_principal
    app.dependency_overrides[get_async_db] = dummy_db

    mock_coder = MagicMock()
    mock_coder.async_decode = AsyncMock(
        return_value={"scope": "profile email address phone"}
    )

    headers = {"Authorization": "Bearer token"}
    with patch("auto_authn.v2.oidc_userinfo.JWTCoder.default", return_value=mock_coder):
        resp = await async_client.get("/userinfo", headers=headers)

    app.dependency_overrides.pop(get_current_principal, None)
    app.dependency_overrides.pop(get_async_db, None)

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.unit
@pytest.mark.asyncio
async def test_userinfo_signed_jwt(async_client):
    @dataclass
    class DummyUser:
        id: str
        tenant_id: str

    user = DummyUser(id="1", tenant_id="1")
    user.username = "bob"
    user.email = "bob@example.com"

    async def override_get_current_principal(*args, **kwargs):
        return user

    async def dummy_db():
        yield MagicMock()

    app.dependency_overrides[get_current_principal] = override_get_current_principal
    app.dependency_overrides[get_async_db] = dummy_db

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
    app.dependency_overrides.pop(get_async_db, None)

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
