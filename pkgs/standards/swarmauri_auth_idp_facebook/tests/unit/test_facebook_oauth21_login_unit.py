import json

import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_facebook import FacebookOAuth21Login


@pytest.fixture
def login() -> FacebookOAuth21Login:
    return FacebookOAuth21Login(
        client_id="app-id",
        client_secret=SecretStr("app-secret"),
        redirect_uri="https://app.example.com/callback",
        state_secret=b"state-secret",
    )


@pytest.mark.unit
def test_resource(login: FacebookOAuth21Login) -> None:
    assert login.resource == "OAuth21Login"


@pytest.mark.unit
def test_type(login: FacebookOAuth21Login) -> None:
    assert login.type == "FacebookOAuth21Login"


@pytest.mark.unit
def test_serialization(login: FacebookOAuth21Login) -> None:
    payload = json.loads(login.model_dump_json())
    restored = FacebookOAuth21Login.model_construct(**payload)
    restored.client_secret = login.client_secret
    assert restored.id == login.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_includes_pkce(login: FacebookOAuth21Login) -> None:
    payload = await login.auth_url()
    assert "code_challenge_method=S256" in payload["url"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_uses_id_token_when_present(
    login: FacebookOAuth21Login, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def fake_exchange_tokens(code: str, state: str):
        return {"id_token": "id-token"}

    async def fake_claims_from_id_token(id_token):
        assert id_token == "id-token"
        return {"sub": "user-id", "email": "user@example.com", "name": "Example"}

    monkeypatch.setattr(login, "_exchange_tokens", fake_exchange_tokens)
    monkeypatch.setattr(login, "_claims_from_id_token", fake_claims_from_id_token)

    payload = await login.auth_url()
    result = await login.exchange_and_identity("code", payload["state"])
    assert result["issuer"] == "facebook-oauth21"
    assert result["sub"] == "user-id"
    assert result["email"] == "user@example.com"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_falls_back_to_profile(
    login: FacebookOAuth21Login, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def fake_exchange_tokens(code: str, state: str):
        return {"access_token": "access-token"}

    async def fake_claims_from_id_token(id_token):
        return None

    async def fake_fetch_profile(access_token: str):
        return {"id": "321", "name": "Fallback User"}

    monkeypatch.setattr(login, "_exchange_tokens", fake_exchange_tokens)
    monkeypatch.setattr(login, "_claims_from_id_token", fake_claims_from_id_token)
    monkeypatch.setattr(login, "_fetch_profile", fake_fetch_profile)

    payload = await login.auth_url()
    result = await login.exchange_and_identity("code", payload["state"])
    assert result["sub"] == "321"
    assert result["name"] == "Fallback User"
