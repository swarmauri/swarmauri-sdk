import json

import pytest
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_okta import OktaOAuth20Login


@pytest.fixture
def login() -> OktaOAuth20Login:
    instance = OktaOAuth20Login(
        issuer="https://okta.example/oauth2/default",
        client_id="client",
        client_secret=SecretStr("secret"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"state-secret"),
    )
    instance.discovery_cache = {
        "authorization_endpoint": "https://okta.example/oauth2/default/v1/authorize",
        "token_endpoint": "https://okta.example/oauth2/default/v1/token",
        "userinfo_endpoint": "https://okta.example/oauth2/default/v1/userinfo",
    }
    return instance


@pytest.mark.unit
def test_resource(login: OktaOAuth20Login) -> None:
    assert login.resource == "OAuth20Login"


@pytest.mark.unit
def test_type(login: OktaOAuth20Login) -> None:
    assert login.type == "OktaOAuth20Login"


@pytest.mark.unit
def test_serialization(login: OktaOAuth20Login) -> None:
    serialized = login.model_dump_json()
    payload = json.loads(serialized)

    restored = OktaOAuth20Login.model_construct(**payload)
    restored.client_secret = login.client_secret
    restored.state_secret = login.state_secret
    restored.discovery_cache = login.discovery_cache

    assert restored.id == login.id
    assert restored.resource == login.resource
    assert restored.type == login.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_contains_okta(login: OktaOAuth20Login) -> None:
    payload = await login.auth_url()
    assert payload["url"].startswith(
        "https://okta.example/oauth2/default/v1/authorize?"
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_invalid_state(login: OktaOAuth20Login) -> None:
    with pytest.raises(ValueError):
        await login.exchange_and_identity("code", "invalid-state")
