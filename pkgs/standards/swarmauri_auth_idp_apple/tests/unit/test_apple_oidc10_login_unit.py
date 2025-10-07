import json

import pytest
from pydantic import SecretBytes

from swarmauri_auth_idp_apple import AppleOIDC10Login


@pytest.fixture
def login() -> AppleOIDC10Login:
    instance = AppleOIDC10Login(
        team_id="team",
        key_id="key",
        client_id="client",
        private_key_pem=SecretBytes(b"dummy"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"state-secret"),
    )
    instance._discovery = {
        "authorization_endpoint": "https://apple.example/authorize",
        "token_endpoint": "https://apple.example/token",
        "jwks_uri": "https://apple.example/keys",
    }
    return instance


@pytest.mark.unit
def test_resource(login: AppleOIDC10Login) -> None:
    assert login.resource == "OIDC10Login"


@pytest.mark.unit
def test_type(login: AppleOIDC10Login) -> None:
    assert login.type == "AppleOIDC10Login"


@pytest.mark.unit
def test_initialization(login: AppleOIDC10Login) -> None:
    assert isinstance(login.id, str)


@pytest.mark.unit
def test_serialization(login: AppleOIDC10Login) -> None:
    serialized = login.model_dump_json()
    data = json.loads(serialized)

    restored = AppleOIDC10Login.model_construct(**data)
    restored.private_key_pem = login.private_key_pem
    restored.state_secret = login.state_secret
    restored._discovery = login._discovery

    assert restored.id == login.id
    assert restored.resource == login.resource
    assert restored.type == login.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_uses_discovery(login: AppleOIDC10Login) -> None:
    payload = await login.auth_url()
    assert payload["url"].startswith("https://apple.example/authorize?")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_invalid_state(login: AppleOIDC10Login) -> None:
    with pytest.raises(ValueError):
        await login.exchange("code", "invalid-state")
