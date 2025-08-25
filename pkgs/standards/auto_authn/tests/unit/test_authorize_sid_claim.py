import uuid
from urllib.parse import parse_qs, urlparse

import nest_asyncio
import pytest
from fastapi import status

from auto_authn.v2.crypto import hash_pw
from auto_authn.v2.orm.tables import Client, Tenant, User
from auto_authn.v2.oidc_id_token import verify_id_token
from auto_authn.v2.rfc8414 import ISSUER

nest_asyncio.apply()


@pytest.mark.usefixtures("temp_key_file")
@pytest.mark.unit
@pytest.mark.asyncio
async def test_authorize_includes_sid_claim(async_client, db_session):
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

    params = {
        "response_type": "id_token",
        "client_id": str(client_id),
        "redirect_uri": "https://client.example/cb",
        "scope": "openid",
        "nonce": "n",
        "username": "alice",
        "password": "password",
        "response_mode": "fragment",
        "prompt": "login",
        "max_age": "3600",
        "login_hint": "alice",
        "claims": "{}",
    }
    resp = await async_client.get("/authorize", params=params, follow_redirects=False)
    assert resp.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    query = parse_qs(urlparse(resp.headers["location"]).query)
    id_token = query["id_token"][0]
    claims = verify_id_token(id_token, issuer=ISSUER, audience=str(client_id))
    assert "sid" in claims
    assert async_client.cookies.get("sid") == claims["sid"]
