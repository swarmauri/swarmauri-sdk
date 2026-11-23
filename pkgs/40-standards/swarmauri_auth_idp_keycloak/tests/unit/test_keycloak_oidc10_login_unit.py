import json

import pytest
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_keycloak import KeycloakOIDC10Login


@pytest.fixture
def login() -> KeycloakOIDC10Login:
    instance = KeycloakOIDC10Login(
        issuer="https://kc.example/realms/myrealm",
        client_id="client",
        client_secret=SecretStr("secret"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"state-secret"),
    )
    instance.discovery_cache = {
        "authorization_endpoint": "https://kc.example/realms/myrealm/protocol/openid-connect/auth",
        "token_endpoint": "https://kc.example/realms/myrealm/protocol/openid-connect/token",
        "jwks_uri": "https://kc.example/realms/myrealm/protocol/openid-connect/certs",
        "userinfo_endpoint": "https://kc.example/realms/myrealm/protocol/openid-connect/userinfo",
    }
    return instance


@pytest.mark.unit
def test_resource(login: KeycloakOIDC10Login) -> None:
    assert login.resource == "OIDC10Login"


@pytest.mark.unit
def test_type(login: KeycloakOIDC10Login) -> None:
    assert login.type == "KeycloakOIDC10Login"


@pytest.mark.unit
def test_serialization(login: KeycloakOIDC10Login) -> None:
    payload = json.loads(login.model_dump_json())

    restored = KeycloakOIDC10Login.model_construct(**payload)
    restored.client_secret = login.client_secret
    restored.state_secret = login.state_secret
    restored.discovery_cache = login.discovery_cache

    assert restored.id == login.id
    assert restored.resource == login.resource
    assert restored.type == login.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_uses_discovery(login: KeycloakOIDC10Login) -> None:
    payload = await login.auth_url()
    assert payload["url"].startswith(
        "https://kc.example/realms/myrealm/protocol/openid-connect/auth?"
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_invalid_state(login: KeycloakOIDC10Login) -> None:
    with pytest.raises(ValueError):
        await login.exchange("code", "invalid-state")
