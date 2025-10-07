import json

import pytest
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_google import GoogleOAuth20Login


@pytest.fixture
def login() -> GoogleOAuth20Login:
    return GoogleOAuth20Login(
        client_id="client",
        client_secret=SecretStr("secret"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"state-secret"),
    )


@pytest.mark.unit
def test_resource(login: GoogleOAuth20Login) -> None:
    assert login.resource == "OAuth20Login"


@pytest.mark.unit
def test_type(login: GoogleOAuth20Login) -> None:
    assert login.type == "GoogleOAuth20Login"


@pytest.mark.unit
def test_serialization(login: GoogleOAuth20Login) -> None:
    serialized = login.model_dump_json()
    payload = json.loads(serialized)

    restored = GoogleOAuth20Login.model_construct(**payload)
    restored.client_secret = login.client_secret
    restored.state_secret = login.state_secret

    assert restored.id == login.id
    assert restored.resource == login.resource
    assert restored.type == login.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_contains_google(login: GoogleOAuth20Login) -> None:
    payload = await login.auth_url()
    assert payload["url"].startswith("https://accounts.google.com/o/oauth2/v2/auth?")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_invalid_state(login: GoogleOAuth20Login) -> None:
    with pytest.raises(ValueError):
        await login.exchange_and_identity("code", "invalid-state")
