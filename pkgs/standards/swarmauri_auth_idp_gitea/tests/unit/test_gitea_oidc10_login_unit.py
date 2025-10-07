import json

import pytest
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_gitea import GiteaOIDC10Login


@pytest.fixture
def login() -> GiteaOIDC10Login:
    instance = GiteaOIDC10Login(
        issuer="https://gitea.example",
        client_id="client",
        client_secret=SecretStr("secret"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"state-secret"),
    )
    instance._discovery = {
        "authorization_endpoint": "https://gitea.example/authorize",
        "token_endpoint": "https://gitea.example/token",
        "jwks_uri": "https://gitea.example/jwks",
    }
    return instance


@pytest.mark.unit
def test_resource(login: GiteaOIDC10Login) -> None:
    assert login.resource == "OIDC10Login"


@pytest.mark.unit
def test_type(login: GiteaOIDC10Login) -> None:
    assert login.type == "GiteaOIDC10Login"


@pytest.mark.unit
def test_serialization(login: GiteaOIDC10Login) -> None:
    serialized = login.model_dump_json()
    data = json.loads(serialized)

    restored = GiteaOIDC10Login.model_construct(**data)
    restored.client_secret = login.client_secret
    restored.state_secret = login.state_secret
    restored._discovery = login._discovery

    assert restored.id == login.id
    assert restored.resource == login.resource
    assert restored.type == login.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_uses_discovery(login: GiteaOIDC10Login) -> None:
    payload = await login.auth_url()
    assert payload["url"].startswith("https://gitea.example/authorize?")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_invalid_state(login: GiteaOIDC10Login) -> None:
    with pytest.raises(ValueError):
        await login.exchange("code", "invalid-state")
