import json

import pytest
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_cognito import CognitoOAuth21Login


@pytest.fixture
def login() -> CognitoOAuth21Login:
    instance = CognitoOAuth21Login(
        issuer="https://cognito.example",
        client_id="client",
        client_secret=SecretStr("secret"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"state-secret"),
    )
    instance._discovery = {
        "authorization_endpoint": "https://cognito.example/authorize",
        "token_endpoint": "https://cognito.example/token",
        "jwks_uri": "https://cognito.example/jwks",
    }
    return instance


@pytest.mark.unit
def test_resource(login: CognitoOAuth21Login) -> None:
    assert login.resource == "OAuth21Login"


@pytest.mark.unit
def test_type(login: CognitoOAuth21Login) -> None:
    assert login.type == "CognitoOAuth21Login"


@pytest.mark.unit
def test_serialization(login: CognitoOAuth21Login) -> None:
    serialized = login.model_dump_json()
    data = json.loads(serialized)

    restored = CognitoOAuth21Login.model_construct(**data)
    restored.client_secret = login.client_secret
    restored.state_secret = login.state_secret
    restored._discovery = login._discovery

    assert restored.id == login.id
    assert restored.resource == login.resource
    assert restored.type == login.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_uses_discovery(login: CognitoOAuth21Login) -> None:
    payload = await login.auth_url()
    assert payload["url"].startswith("https://cognito.example/authorize?")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_invalid_state(login: CognitoOAuth21Login) -> None:
    with pytest.raises(ValueError):
        await login.exchange_and_identity("code", "invalid-state")
