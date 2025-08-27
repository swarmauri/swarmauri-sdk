import uuid
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi import status

from auto_authn.v2.crypto import hash_pw
from auto_authn.v2.orm.tables import Client, Tenant, User, AuthSession
from auto_authn.v2.routers.shared import SESSIONS


async def _setup(async_client, db_session):
    tenant_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    tenant = Tenant(
        id=tenant_id,
        name="T",
        email="t@example.com",
        slug="t",
        created_at=now,
        updated_at=now,
    )
    client_id = uuid.uuid4()
    client = Client(
        id=client_id,
        tenant_id=tenant_id,
        client_secret_hash=hash_pw("secret"),
        redirect_uris="https://client.example/cb",
        created_at=now,
        updated_at=now,
        is_active=True,
    )
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        tenant_id=tenant_id,
        username="alice",
        email="alice@example.com",
        password_hash=hash_pw("password"),
        created_at=now,
        updated_at=now,
        is_active=True,
    )
    session_id = str(uuid.uuid4())
    session = AuthSession(
        id=session_id,
        tenant_id=tenant_id,
        user_id=user.id,
        username="alice",
        auth_time=now,
        created_at=now,
        updated_at=now,
    )
    db_session.add_all([tenant, client, user, session])
    await db_session.commit()
    SESSIONS[session_id] = {
        "sub": str(user_id),
        "tid": str(tenant_id),
        "username": "alice",
        "auth_time": now,
    }
    async_client.cookies.set("sid", session_id)
    return str(client_id)


@pytest.mark.usefixtures("temp_key_file")
@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.xfail(reason="Authorization flow pending", strict=False)
async def test_authorize_response_mode_query(async_client, db_session):
    client_id = await _setup(async_client, db_session)
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": "https://client.example/cb",
        "scope": "openid",
        "state": "xyz",
        "response_mode": "query",
        "login_hint": "alice",
    }
    resp = await async_client.get("/authorize", params=params, follow_redirects=False)
    assert resp.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    qs = parse_qs(urlparse(resp.headers["location"]).query)
    assert "code" in qs
    assert qs.get("state", [None])[0] == "xyz"


@pytest.mark.usefixtures("temp_key_file")
@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.xfail(reason="Authorization flow pending", strict=False)
async def test_authorize_response_mode_fragment(async_client, db_session):
    client_id = await _setup(async_client, db_session)
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": "https://client.example/cb",
        "scope": "openid",
        "state": "abc",
        "response_mode": "fragment",
    }
    resp = await async_client.get("/authorize", params=params, follow_redirects=False)
    assert resp.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    frag = urlparse(resp.headers["location"]).fragment
    qs = parse_qs(frag)
    assert "code" in qs
    assert qs.get("state", [None])[0] == "abc"


@pytest.mark.usefixtures("temp_key_file")
@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.xfail(reason="Authorization flow pending", strict=False)
async def test_authorize_response_mode_form_post(async_client, db_session):
    client_id = await _setup(async_client, db_session)
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": "https://client.example/cb",
        "scope": "openid",
        "state": "form",
        "response_mode": "form_post",
    }
    resp = await async_client.get("/authorize", params=params, follow_redirects=False)
    assert resp.status_code == status.HTTP_200_OK
    assert '<form method="post" action="https://client.example/cb">' in resp.text
    assert 'name="code"' in resp.text
    assert 'name="state"' in resp.text
