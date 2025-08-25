import pytest
from urllib.parse import parse_qs, urlparse
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from auto_authn.v2.orm.tables import Tenant, User, Client
from auto_authn.v2.crypto import hash_pw


async def _prepare(db: AsyncSession) -> None:
    tenant = Tenant(slug="t1", name="T1", email="t1@example.com")
    db.add(tenant)
    await db.commit()
    user = User(
        tenant_id=tenant.id,
        username="alice",
        email="alice@example.com",
        password_hash=hash_pw("Passw0rd!"),
    )
    db.add(user)
    await db.commit()
    client = Client.new(
        tenant_id=tenant.id,
        client_id="client123",
        client_secret="secret",
        redirects=["https://client.example.com/cb"],
    )
    db.add(client)
    await db.commit()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_authorize_token_flow(
    async_client: AsyncClient, db_session: AsyncSession
):
    await _prepare(db_session)
    params = {
        "response_type": "token",
        "client_id": "client123",
        "redirect_uri": "https://client.example.com/cb",
        "scope": "openid",
        "state": "xyz",
        "username": "alice",
        "password": "Passw0rd!",
    }
    resp = await async_client.get("/authorize", params=params, follow_redirects=False)
    assert resp.status_code in {302, 307}
    qs = parse_qs(urlparse(resp.headers["location"]).query)
    assert "access_token" in qs
    assert qs.get("token_type", [None])[0] == "bearer"
    assert qs.get("state", [None])[0] == "xyz"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_authorize_id_token_requires_nonce(
    async_client: AsyncClient, db_session: AsyncSession
):
    await _prepare(db_session)
    params = {
        "response_type": "id_token",
        "client_id": "client123",
        "redirect_uri": "https://client.example.com/cb",
        "scope": "openid",
        "username": "alice",
        "password": "Passw0rd!",
    }
    resp = await async_client.get("/authorize", params=params, follow_redirects=False)
    assert resp.status_code == 400
    params["nonce"] = "n-0S6_WzA2Mj"
    resp2 = await async_client.get("/authorize", params=params, follow_redirects=False)
    assert resp2.status_code in {302, 307}
    qs = parse_qs(urlparse(resp2.headers["location"]).query)
    assert "id_token" in qs


@pytest.mark.integration
@pytest.mark.asyncio
async def test_authorize_requires_openid_scope(
    async_client: AsyncClient, db_session: AsyncSession
):
    await _prepare(db_session)
    params = {
        "response_type": "code",
        "client_id": "client123",
        "redirect_uri": "https://client.example.com/cb",
        "scope": "profile",  # missing openid
        "username": "alice",
        "password": "Passw0rd!",
    }
    resp = await async_client.get("/authorize", params=params, follow_redirects=False)
    assert resp.status_code == 400
    assert resp.json()["error"] == "invalid_scope"
