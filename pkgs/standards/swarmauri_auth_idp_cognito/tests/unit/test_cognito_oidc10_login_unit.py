import json

import pytest
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_cognito import CognitoOIDC10Login


@pytest.fixture
def login() -> CognitoOIDC10Login:
    instance = CognitoOIDC10Login(
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
def test_resource(login: CognitoOIDC10Login) -> None:
    assert login.resource == "OIDC10Login"


@pytest.mark.unit
def test_type(login: CognitoOIDC10Login) -> None:
    assert login.type == "CognitoOIDC10Login"


@pytest.mark.unit
def test_serialization(login: CognitoOIDC10Login) -> None:
    serialized = login.model_dump_json()
    data = json.loads(serialized)

    restored = CognitoOIDC10Login.model_construct(**data)
    restored.client_secret = login.client_secret
    restored.state_secret = login.state_secret
    restored._discovery = login._discovery

    assert restored.id == login.id
    assert restored.resource == login.resource
    assert restored.type == login.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_uses_discovery(login: CognitoOIDC10Login) -> None:
    payload = await login.auth_url()
    assert payload["url"].startswith("https://cognito.example/authorize?")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_invalid_state(login: CognitoOIDC10Login) -> None:
    with pytest.raises(ValueError):
        await login.exchange("code", "invalid-state")
