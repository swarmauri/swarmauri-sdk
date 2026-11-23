import json

import pytest
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_gitlab import GitLabOIDC10Login


@pytest.fixture
def login() -> GitLabOIDC10Login:
    instance = GitLabOIDC10Login(
        issuer="https://gitlab.example",
        client_id="client",
        client_secret=SecretStr("secret"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"state-secret"),
    )
    instance.discovery_cache = {
        "authorization_endpoint": "https://gitlab.example/oauth/authorize",
        "token_endpoint": "https://gitlab.example/oauth/token",
        "jwks_uri": "https://gitlab.example/oauth/jwks",
    }
    return instance


@pytest.mark.unit
def test_resource(login: GitLabOIDC10Login) -> None:
    assert login.resource == "OIDC10Login"


@pytest.mark.unit
def test_type(login: GitLabOIDC10Login) -> None:
    assert login.type == "GitLabOIDC10Login"


@pytest.mark.unit
def test_serialization(login: GitLabOIDC10Login) -> None:
    serialized = login.model_dump_json()
    payload = json.loads(serialized)

    restored = GitLabOIDC10Login.model_construct(**payload)
    restored.client_secret = login.client_secret
    restored.state_secret = login.state_secret
    restored.discovery_cache = login.discovery_cache

    assert restored.id == login.id
    assert restored.resource == login.resource
    assert restored.type == login.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_uses_discovery(login: GitLabOIDC10Login) -> None:
    payload = await login.auth_url()
    assert payload["url"].startswith("https://gitlab.example/oauth/authorize?")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_invalid_state(login: GitLabOIDC10Login) -> None:
    with pytest.raises(ValueError):
        await login.exchange("code", "invalid-state")
