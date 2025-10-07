import json

import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_azure import AzureOAuth20Login


@pytest.fixture
def login() -> AzureOAuth20Login:
    return AzureOAuth20Login(
        tenant="organizations",
        client_id="client-id",
        client_secret=SecretStr("client-secret"),
        redirect_uri="https://app.example.com/callback",
        state_secret=b"state-secret",
    )


@pytest.mark.unit
def test_resource(login: AzureOAuth20Login) -> None:
    assert login.resource == "OAuth20Login"


@pytest.mark.unit
def test_type(login: AzureOAuth20Login) -> None:
    assert login.type == "AzureOAuth20Login"


@pytest.mark.unit
def test_serialization(login: AzureOAuth20Login) -> None:
    dumped = json.loads(login.model_dump_json())
    cloned = AzureOAuth20Login.model_construct(**dumped)
    cloned.client_secret = login.client_secret
    assert cloned.id == login.id
    assert cloned.client_id == login.client_id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_contains_pkce(login: AzureOAuth20Login) -> None:
    payload = await login.auth_url()
    assert "code_challenge_method=S256" in payload["url"]
    assert payload["state"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_and_identity_returns_profile(
    login: AzureOAuth20Login, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def fake_exchange_tokens(code: str, state: str):
        assert code == "auth-code"
        assert state
        return {"access_token": "access-token"}

    async def fake_fetch_profile(access_token: str):
        assert access_token == "access-token"
        return {
            "id": "user-id",
            "mail": "user@example.com",
            "displayName": "Example User",
        }

    monkeypatch.setattr(login, "_exchange_tokens", fake_exchange_tokens)
    monkeypatch.setattr(login, "_fetch_profile", fake_fetch_profile)

    payload = await login.auth_url()
    result = await login.exchange_and_identity("auth-code", payload["state"])
    assert result["issuer"] == "azure-oauth20"
    assert result["tokens"] == {"access_token": "access-token"}
    assert result["profile"]["id"] == "user-id"
    assert result["email"] == "user@example.com"
    assert result["name"] == "Example User"
