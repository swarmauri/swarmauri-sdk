import uuid

import pytest
from fastapi import status

from auto_authn.v2.crypto import hash_pw
from auto_authn.v2.orm.tables import Client, Tenant, User


@pytest.mark.usefixtures("temp_key_file")
@pytest.mark.unit
@pytest.mark.asyncio
async def test_authorize_requires_openid_scope(async_client, db_session):
    tenant_id = uuid.uuid4()
    tenant = Tenant(id=tenant_id, name="T1", email="t1@example.com")
    client = Client(
        id="client1",
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
        "client_id": "client1",
        "redirect_uri": "https://client.example/cb",
        "scope": "profile",
        "username": "alice",
        "password": "password",
    }
    resp = await async_client.get("/authorize", params=params, follow_redirects=False)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()["error"] == "invalid_scope"
