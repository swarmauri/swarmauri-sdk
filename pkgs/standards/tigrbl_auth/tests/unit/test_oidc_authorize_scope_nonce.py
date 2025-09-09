import json
import uuid
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi import status

from tigrbl_auth.crypto import hash_pw
from tigrbl_auth.orm import Client, Tenant, User
from tigrbl_auth.oidc_discovery import ISSUER
from tigrbl_auth.oidc_id_token import verify_id_token
from tigrbl_auth.routers.auth_flows import AUTH_CODES, SESSIONS


@pytest.mark.usefixtures("temp_key_file")
@pytest.mark.unit
@pytest.mark.asyncio
async def test_authorize_requires_openid_scope(async_client, db_session):
    tenant_id = uuid.uuid4()
    tenant = Tenant(id=tenant_id, name="T", email="t@example.com", slug="t")
    client_id = uuid.uuid4()
    client = Client(
        id=client_id,
        tenant_id=tenant_id,
        client_secret_hash=hash_pw("secret"),
        redirect_uris="https://client.example/cb",
    )
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        username="alice",
        email="alice@example.com",
        password_hash=hash_pw("password"),
    )
    db_session.add_all([tenant, client, user])
    await db_session.commit()

    await async_client.post(
        "/login", json={"identifier": "alice", "password": "password"}
    )

    params = {
        "response_type": "code",
        "client_id": str(client_id),
        "redirect_uri": "https://client.example/cb",
        "scope": "profile",
    }
    resp = await async_client.get("/authorize", params=params, follow_redirects=False)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()["detail"]["error"] == "invalid_scope"


@pytest.mark.usefixtures("temp_key_file")
@pytest.mark.unit
@pytest.mark.asyncio
async def test_authorize_persists_nonce(async_client, db_session):
    tenant_id = uuid.uuid4()
    tenant = Tenant(id=tenant_id, name="T2", email="t2@example.com", slug="t2")
    client_id = uuid.uuid4()
    client = Client(
        id=client_id,
        tenant_id=tenant_id,
        client_secret_hash=hash_pw("secret"),
        redirect_uris="https://client.example/cb",
    )
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        username="bob",
        email="bob@example.com",
        password_hash=hash_pw("password"),
    )
    db_session.add_all([tenant, client, user])
    await db_session.commit()

    await async_client.post(
        "/login", json={"identifier": "bob", "password": "password"}
    )

    params = {
        "response_type": "code",
        "client_id": str(client_id),
        "redirect_uri": "https://client.example/cb",
        "scope": "openid",
        "nonce": "n-0S6_WzA2Mj",
        "login_hint": "bob",
    }
    resp = await async_client.get("/authorize", params=params, follow_redirects=False)
    assert resp.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    query = parse_qs(urlparse(resp.headers["location"]).query)
    code = query["code"][0]
    try:
        assert AUTH_CODES[code]["nonce"] == "n-0S6_WzA2Mj"
    finally:
        AUTH_CODES.clear()


@pytest.mark.usefixtures("temp_key_file")
@pytest.mark.unit
@pytest.mark.asyncio
async def test_authorize_prompt_login_requires_reauth(async_client, db_session):
    tenant_id = uuid.uuid4()
    tenant = Tenant(id=tenant_id, name="T3", email="t3@example.com", slug="t3")
    client_id = uuid.uuid4()
    client = Client(
        id=client_id,
        tenant_id=tenant_id,
        client_secret_hash=hash_pw("secret"),
        redirect_uris="https://client.example/cb",
    )
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        username="carol",
        email="carol@example.com",
        password_hash=hash_pw("password"),
    )
    db_session.add_all([tenant, client, user])
    await db_session.commit()

    await async_client.post(
        "/login", json={"identifier": "carol", "password": "password"}
    )

    params = {
        "response_type": "code",
        "client_id": str(client_id),
        "redirect_uri": "https://client.example/cb",
        "scope": "openid",
        "prompt": "login",
    }
    resp = await async_client.get("/authorize", params=params, follow_redirects=False)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp.json()["detail"]["error"] == "login_required"


@pytest.mark.usefixtures("temp_key_file")
@pytest.mark.unit
@pytest.mark.asyncio
async def test_authorize_login_hint_mismatch_requires_reauth(async_client, db_session):
    tenant_id = uuid.uuid4()
    tenant = Tenant(id=tenant_id, name="T5", email="t5@example.com", slug="t5")
    client_id = uuid.uuid4()
    client = Client(
        id=client_id,
        tenant_id=tenant_id,
        client_secret_hash=hash_pw("secret"),
        redirect_uris="https://client.example/cb",
    )
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        username="erin",
        email="erin@example.com",
        password_hash=hash_pw("password"),
    )
    db_session.add_all([tenant, client, user])
    await db_session.commit()

    await async_client.post(
        "/login", json={"identifier": "erin", "password": "password"}
    )

    params = {
        "response_type": "code",
        "client_id": str(client_id),
        "redirect_uri": "https://client.example/cb",
        "scope": "openid",
        "login_hint": "not_erin",
    }
    resp = await async_client.get("/authorize", params=params, follow_redirects=False)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp.json()["detail"]["error"] == "login_required"


@pytest.mark.usefixtures("temp_key_file")
@pytest.mark.unit
@pytest.mark.asyncio
async def test_authorize_claims_in_id_token(async_client, db_session):
    tenant_id = uuid.uuid4()
    tenant = Tenant(id=tenant_id, name="T6", email="t6@example.com", slug="t6")
    client_id = uuid.uuid4()
    client = Client(
        id=client_id,
        tenant_id=tenant_id,
        client_secret_hash=hash_pw("secret"),
        redirect_uris="https://client.example/cb",
    )
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        username="frank",
        email="frank@example.com",
        password_hash=hash_pw("password"),
    )
    db_session.add_all([tenant, client, user])
    await db_session.commit()

    await async_client.post(
        "/login", json={"identifier": "frank", "password": "password"}
    )

    claims_req = json.dumps({"id_token": {"email": {"essential": True}}})
    params = {
        "response_type": "id_token",
        "client_id": str(client_id),
        "redirect_uri": "https://client.example/cb",
        "scope": "openid email",
        "nonce": "n-1",
        "claims": claims_req,
    }
    resp = await async_client.get("/authorize", params=params, follow_redirects=False)
    assert resp.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    frag = urlparse(resp.headers["location"]).fragment
    qs = parse_qs(frag)
    token = qs["id_token"][0]
    claims = await verify_id_token(token, issuer=ISSUER, audience=str(client_id))
    assert claims["email"] == "frank@example.com"


@pytest.mark.usefixtures("temp_key_file")
@pytest.mark.unit
@pytest.mark.asyncio
async def test_authorize_max_age_requires_recent_login(async_client, db_session):
    tenant_id = uuid.uuid4()
    tenant = Tenant(id=tenant_id, name="T4", email="t4@example.com", slug="t4")
    client_id = uuid.uuid4()
    client = Client(
        id=client_id,
        tenant_id=tenant_id,
        client_secret_hash=hash_pw("secret"),
        redirect_uris="https://client.example/cb",
    )
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        username="dave",
        email="dave@example.com",
        password_hash=hash_pw("password"),
    )
    db_session.add_all([tenant, client, user])
    await db_session.commit()

    resp = await async_client.post(
        "/login", json={"identifier": "dave", "password": "password"}
    )
    sid = resp.cookies.get("sid")
    assert sid in SESSIONS
    SESSIONS[sid]["auth_time"] = datetime.utcnow() - timedelta(seconds=31)

    params = {
        "response_type": "code",
        "client_id": str(client_id),
        "redirect_uri": "https://client.example/cb",
        "scope": "openid",
        "max_age": 30,
    }
    resp = await async_client.get("/authorize", params=params, follow_redirects=False)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp.json()["detail"]["error"] == "login_required"
