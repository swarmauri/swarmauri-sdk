import uuid
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi import status

from auto_authn.v2.crypto import hash_pw
from auto_authn.v2.orm.tables import Client, Tenant, User
from auto_authn.v2.routers.auth_flows import AUTH_CODES


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

    params = {
        "response_type": "code",
        "client_id": str(client_id),
        "redirect_uri": "https://client.example/cb",
        "scope": "profile",
        "username": "alice",
        "password": "password",
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

    params = {
        "response_type": "code",
        "client_id": str(client_id),
        "redirect_uri": "https://client.example/cb",
        "scope": "openid",
        "nonce": "n-0S6_WzA2Mj",
        "username": "bob",
        "password": "password",
    }
    resp = await async_client.get("/authorize", params=params, follow_redirects=False)
    assert resp.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    query = parse_qs(urlparse(resp.headers["location"]).query)
    code = query["code"][0]
    try:
        assert AUTH_CODES[code]["nonce"] == "n-0S6_WzA2Mj"
    finally:
        AUTH_CODES.clear()
