import json

import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_facebook import FacebookOAuth20Login


@pytest.fixture
def login() -> FacebookOAuth20Login:
    return FacebookOAuth20Login(
        client_id="app-id",
        client_secret=SecretStr("app-secret"),
        redirect_uri="https://app.example.com/callback",
        state_secret=b"state-secret",
    )


@pytest.mark.unit
def test_resource(login: FacebookOAuth20Login) -> None:
    assert login.resource == "OAuth20Login"


@pytest.mark.unit
def test_type(login: FacebookOAuth20Login) -> None:
    assert login.type == "FacebookOAuth20Login"


@pytest.mark.unit
def test_serialization(login: FacebookOAuth20Login) -> None:
    dumped = json.loads(login.model_dump_json())
    restored = FacebookOAuth20Login.model_construct(**dumped)
    restored.client_secret = login.client_secret
    assert restored.id == login.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_contains_pkce(login: FacebookOAuth20Login) -> None:
    payload = await login.auth_url()
    assert "code_challenge_method=S256" in payload["url"]
    assert payload["state"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_and_identity_returns_profile(
    login: FacebookOAuth20Login, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def fake_exchange_tokens(code: str, state: str):
        assert code == "auth-code"
        assert state
        return {"access_token": "access-token"}

    async def fake_fetch_profile(access_token: str):
        assert access_token == "access-token"
        return {"id": "123", "email": "user@example.com", "name": "Example User"}

    monkeypatch.setattr(login, "_exchange_tokens", fake_exchange_tokens)
    monkeypatch.setattr(login, "_fetch_profile", fake_fetch_profile)

    payload = await login.auth_url()
    result = await login.exchange_and_identity("auth-code", payload["state"])
    assert result["issuer"] == "facebook-oauth20"
    assert result["sub"] == "123"
    assert result["email"] == "user@example.com"
    assert result["name"] == "Example User"
