import pytest
from sqlalchemy import select

from auto_authn.v2.jwtoken import JWTCoder
from auto_authn.v2.orm.tables import User
from auto_authn.v2.runtime_cfg import settings


@pytest.mark.asyncio
async def test_invite_code_and_attributes(auth_test_client, db_session):
    settings.invite_codes = "CODE123"
    resp = await auth_test_client.client.post(
        "/register",
        json={
            "tenant_slug": "public",
            "username": "user1",
            "email": "u1@example.com",
            "password": "Password1!",
            "invite_code": "WRONG",
        },
    )
    assert resp.status_code == 422

    resp = await auth_test_client.client.post(
        "/register",
        json={
            "tenant_slug": "public",
            "username": "user2",
            "email": "u2@example.com",
            "password": "Password1!",
            "invite_code": "CODE123",
            "attributes": {"role": "tester"},
        },
    )
    assert resp.status_code == 201

    user = await db_session.scalar(select(User).where(User.username == "user2"))
    assert user.attrs == {"role": "tester"}


@pytest.mark.asyncio
async def test_password_policy_enforced(auth_test_client):
    settings.invite_codes = ""
    settings.password_min_length = 12
    settings.password_regex = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).+$"

    resp = await auth_test_client.client.post(
        "/register",
        json={
            "tenant_slug": "public",
            "username": "pass1",
            "email": "p1@example.com",
            "password": "short1A",
        },
    )
    assert resp.status_code == 422

    resp = await auth_test_client.client.post(
        "/register",
        json={
            "tenant_slug": "public",
            "username": "pass2",
            "email": "p2@example.com",
            "password": "Longpassword",
        },
    )
    assert resp.status_code == 422

    resp = await auth_test_client.client.post(
        "/register",
        json={
            "tenant_slug": "public",
            "username": "pass3",
            "email": "p3@example.com",
            "password": "StrongPass123",
        },
    )
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_session_ttl_configurable(auth_test_client):
    settings.invite_codes = ""
    settings.password_min_length = 3
    settings.password_regex = None
    settings.session_access_ttl_minutes = 5
    settings.session_refresh_ttl_minutes = 10

    resp = await auth_test_client.client.post(
        "/register",
        json={
            "tenant_slug": "public",
            "username": "ttluser",
            "email": "ttl@example.com",
            "password": "Good123",
        },
    )
    assert resp.status_code == 201
    tokens = resp.json()
    coder = JWTCoder.default()
    access_claims = await coder.async_decode(tokens["access_token"])
    refresh_claims = await coder.async_decode(tokens["refresh_token"])
    assert access_claims["exp"] - access_claims["iat"] == 5 * 60
    assert refresh_claims["exp"] - refresh_claims["iat"] == 10 * 60
