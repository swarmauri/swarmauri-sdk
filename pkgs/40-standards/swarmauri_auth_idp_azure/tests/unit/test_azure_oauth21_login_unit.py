import json

import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_azure import AzureOAuth21Login


@pytest.fixture
def login() -> AzureOAuth21Login:
    return AzureOAuth21Login(
        tenant="organizations",
        client_id="client-id",
        client_secret=SecretStr("client-secret"),
        redirect_uri="https://app.example.com/callback",
        state_secret=b"state-secret",
    )


@pytest.mark.unit
def test_resource(login: AzureOAuth21Login) -> None:
    assert login.resource == "OAuth21Login"


@pytest.mark.unit
def test_type(login: AzureOAuth21Login) -> None:
    assert login.type == "AzureOAuth21Login"


@pytest.mark.unit
def test_serialization(login: AzureOAuth21Login) -> None:
    payload = json.loads(login.model_dump_json())
    restored = AzureOAuth21Login.model_construct(**payload)
    restored.client_secret = login.client_secret
    assert restored.id == login.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_includes_prompt(login: AzureOAuth21Login) -> None:
    payload = await login.auth_url()
    assert "prompt=select_account" in payload["url"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_and_identity_returns_profile(
    login: AzureOAuth21Login, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def fake_exchange_tokens(code: str, state: str):
        return {"access_token": "access-token"}

    async def fake_fetch_profile(access_token: str):
        return {
            "id": "user-id",
            "userPrincipalName": "user@example.com",
            "displayName": "Example User",
        }

    monkeypatch.setattr(login, "_exchange_tokens", fake_exchange_tokens)
    monkeypatch.setattr(login, "_fetch_profile", fake_fetch_profile)

    payload = await login.auth_url()
    result = await login.exchange_and_identity("code", payload["state"])
    assert result["issuer"] == "azure-oauth21"
    assert result["email"] == "user@example.com"
    assert result["profile"]["displayName"] == "Example User"
