import uuid
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi import status

from auto_authn.crypto import hash_pw
from auto_authn.orm.tables import Client, Tenant, User
from auto_authn.oidc_id_token import oidc_hash, verify_id_token
from auto_authn.rfc8414_metadata import ISSUER
from auto_authn.routers.auth_flows import AUTH_CODES


@pytest.mark.usefixtures("temp_key_file")
@pytest.mark.unit
@pytest.mark.asyncio
async def test_authorize_includes_at_hash(async_client, db_session):
    tenant_id = uuid.uuid4()
    tenant = Tenant(id=tenant_id, name="T1", email="t1@example.com", slug="t1")
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
        "response_type": "token id_token",
        "client_id": str(client_id),
        "redirect_uri": "https://client.example/cb",
        "scope": "openid",
        "nonce": "n",
    }
    resp = await async_client.get("/authorize", params=params, follow_redirects=False)
    assert resp.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    fragment = urlparse(resp.headers["location"]).fragment
    query = parse_qs(fragment)
    access = query["access_token"][0]
    id_token = query["id_token"][0]
    claims = await verify_id_token(id_token, issuer=ISSUER, audience=str(client_id))
    assert claims["at_hash"] == oidc_hash(access)


@pytest.mark.usefixtures("temp_key_file")
@pytest.mark.unit
@pytest.mark.asyncio
async def test_authorize_includes_c_hash(async_client, db_session):
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
        "response_type": "code id_token",
        "client_id": str(client_id),
        "redirect_uri": "https://client.example/cb",
        "scope": "openid",
        "nonce": "n",
    }
    resp = await async_client.get("/authorize", params=params, follow_redirects=False)
    assert resp.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    fragment = urlparse(resp.headers["location"]).fragment
    query = parse_qs(fragment)
    code = query["code"][0]
    id_token = query["id_token"][0]
    claims = await verify_id_token(id_token, issuer=ISSUER, audience=str(client_id))
    assert claims["c_hash"] == oidc_hash(code)
    AUTH_CODES.clear()
