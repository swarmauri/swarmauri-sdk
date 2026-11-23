import json

import pytest
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_okta import OktaOIDC10Login


@pytest.fixture
def login() -> OktaOIDC10Login:
    instance = OktaOIDC10Login(
        issuer="https://okta.example/oauth2/default",
        client_id="client",
        client_secret=SecretStr("secret"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"state-secret"),
    )
    instance.discovery_cache = {
        "authorization_endpoint": "https://okta.example/oauth2/default/v1/authorize",
        "token_endpoint": "https://okta.example/oauth2/default/v1/token",
        "jwks_uri": "https://okta.example/oauth2/default/v1/keys",
        "userinfo_endpoint": "https://okta.example/oauth2/default/v1/userinfo",
    }
    return instance


@pytest.mark.unit
def test_resource(login: OktaOIDC10Login) -> None:
    assert login.resource == "OIDC10Login"


@pytest.mark.unit
def test_type(login: OktaOIDC10Login) -> None:
    assert login.type == "OktaOIDC10Login"


@pytest.mark.unit
def test_serialization(login: OktaOIDC10Login) -> None:
    serialized = login.model_dump_json()
    payload = json.loads(serialized)

    restored = OktaOIDC10Login.model_construct(**payload)
    restored.client_secret = login.client_secret
    restored.state_secret = login.state_secret
    restored.discovery_cache = login.discovery_cache

    assert restored.id == login.id
    assert restored.resource == login.resource
    assert restored.type == login.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_uses_discovery(login: OktaOIDC10Login) -> None:
    payload = await login.auth_url()
    assert payload["url"].startswith(
        "https://okta.example/oauth2/default/v1/authorize?"
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_invalid_state(login: OktaOIDC10Login) -> None:
    with pytest.raises(ValueError):
        await login.exchange("code", "invalid-state")
