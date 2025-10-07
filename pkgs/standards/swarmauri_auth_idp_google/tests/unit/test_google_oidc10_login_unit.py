import json

import pytest
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_google import GoogleOIDC10Login


@pytest.fixture
def login() -> GoogleOIDC10Login:
    instance = GoogleOIDC10Login(
        client_id="client",
        client_secret=SecretStr("secret"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"state-secret"),
    )
    instance.discovery_cache = {
        "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_endpoint": "https://oauth2.googleapis.com/token",
        "jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
    }
    return instance


@pytest.mark.unit
def test_resource(login: GoogleOIDC10Login) -> None:
    assert login.resource == "OIDC10Login"


@pytest.mark.unit
def test_type(login: GoogleOIDC10Login) -> None:
    assert login.type == "GoogleOIDC10Login"


@pytest.mark.unit
def test_serialization(login: GoogleOIDC10Login) -> None:
    serialized = login.model_dump_json()
    payload = json.loads(serialized)

    restored = GoogleOIDC10Login.model_construct(**payload)
    restored.client_secret = login.client_secret
    restored.state_secret = login.state_secret
    restored.discovery_cache = login.discovery_cache

    assert restored.id == login.id
    assert restored.resource == login.resource
    assert restored.type == login.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_uses_discovery(login: GoogleOIDC10Login) -> None:
    payload = await login.auth_url()
    assert payload["url"].startswith("https://accounts.google.com/o/oauth2/v2/auth?")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_invalid_state(login: GoogleOIDC10Login) -> None:
    with pytest.raises(ValueError):
        await login.exchange("code", "invalid-state")
