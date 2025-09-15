import pytest
from httpx import AsyncClient
from urllib.parse import parse_qs, urlparse
from uuid import UUID, uuid4

from tigrbl.engine import HybridSession
from tigrbl_auth.crypto import hash_pw
from tigrbl_auth.orm import Client, Tenant, User
from tigrbl_auth.rfc.rfc7636_pkce import makeCodeChallenge, makeCodeVerifier


@pytest.mark.asyncio
async def test_authorization_code_pkce_flow(
    async_client: AsyncClient, db_session: HybridSession
):
    tenant = Tenant(slug="t1", name="T1", email="t1@example.com")
    db_session.add(tenant)
    await db_session.commit()

    user = User(
        tenant_id=tenant.id,
        username="alice",
        email="alice@example.com",
        password_hash=hash_pw("Passw0rd!"),
    )
    db_session.add(user)
    await db_session.commit()

    client_id = str(uuid4())
    client = Client.new(
        tenant_id=tenant.id,
        client_id=client_id,
        client_secret="secret",
        redirects=["https://client.example.com/cb"],
    )
    db_session.add(client)
    await db_session.commit()

    # Establish session via login
    login_resp = await async_client.post(
        "/login", json={"identifier": "alice", "password": "Passw0rd!"}
    )
    assert login_resp.status_code == 200

    verifier = makeCodeVerifier()
    challenge = makeCodeChallenge(verifier)
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": "https://client.example.com/cb",
        "scope": "openid",
        "state": "xyz",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    resp = await async_client.get("/authorize", params=params, follow_redirects=False)
    assert resp.status_code in {302, 307}
    location = resp.headers["location"]
    qs = parse_qs(urlparse(location).query)
    code = qs["code"][0]
    assert UUID(code)
    assert qs.get("state", [None])[0] == "xyz"

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "https://client.example.com/cb",
        "client_id": client_id,
        "code_verifier": verifier,
    }
    token_resp = await async_client.post("/token", data=data)
    assert token_resp.status_code == 200
    body = token_resp.json()
    assert "access_token" in body and "refresh_token" in body


@pytest.mark.asyncio
async def test_authorization_code_pkce_invalid_verifier(
    async_client: AsyncClient, db_session: HybridSession
):
    tenant = Tenant(slug="t1", name="T1", email="t1@example.com")
    db_session.add(tenant)
    await db_session.commit()

    user = User(
        tenant_id=tenant.id,
        username="alice",
        email="alice@example.com",
        password_hash=hash_pw("Passw0rd!"),
    )
    db_session.add(user)
    await db_session.commit()

    client_id = str(uuid4())
    client = Client.new(
        tenant_id=tenant.id,
        client_id=client_id,
        client_secret="secret",
        redirects=["https://client.example.com/cb"],
    )
    db_session.add(client)
    await db_session.commit()

    login_resp = await async_client.post(
        "/login", json={"identifier": "alice", "password": "Passw0rd!"}
    )
    assert login_resp.status_code == 200

    verifier = makeCodeVerifier()
    challenge = makeCodeChallenge(verifier)
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": "https://client.example.com/cb",
        "scope": "openid",
        "state": "xyz",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    resp = await async_client.get("/authorize", params=params, follow_redirects=False)
    assert resp.status_code in {302, 307}
    qs = parse_qs(urlparse(resp.headers["location"]).query)
    code = qs["code"][0]

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "https://client.example.com/cb",
        "client_id": client_id,
        "code_verifier": "wrong",
    }
    token_resp = await async_client.post("/token", data=data)
    assert token_resp.status_code == 400
    assert token_resp.json()["error"] == "invalid_grant"
