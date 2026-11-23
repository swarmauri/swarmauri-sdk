import json

import pytest
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_cognito import CognitoOAuth20Login


@pytest.fixture
def login() -> CognitoOAuth20Login:
    instance = CognitoOAuth20Login(
        issuer="https://cognito.example",
        client_id="client",
        client_secret=SecretStr("secret"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"state-secret"),
    )
    instance._discovery = {
        "authorization_endpoint": "https://cognito.example/authorize",
        "token_endpoint": "https://cognito.example/token",
        "userinfo_endpoint": "https://cognito.example/userinfo",
    }
    return instance


@pytest.mark.unit
def test_resource(login: CognitoOAuth20Login) -> None:
    assert login.resource == "OAuth20Login"


@pytest.mark.unit
def test_type(login: CognitoOAuth20Login) -> None:
    assert login.type == "CognitoOAuth20Login"


@pytest.mark.unit
def test_serialization(login: CognitoOAuth20Login) -> None:
    serialized = login.model_dump_json()
    data = json.loads(serialized)

    restored = CognitoOAuth20Login.model_construct(**data)
    restored.client_secret = login.client_secret
    restored.state_secret = login.state_secret
    restored._discovery = login._discovery

    assert restored.id == login.id
    assert restored.resource == login.resource
    assert restored.type == login.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_uses_discovery(login: CognitoOAuth20Login) -> None:
    payload = await login.auth_url()
    assert payload["url"].startswith("https://cognito.example/authorize?")
    assert "code_challenge_method=S256" in payload["url"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_invalid_state(login: CognitoOAuth20Login) -> None:
    with pytest.raises(ValueError):
        await login.exchange_and_identity("code", "invalid-state")
