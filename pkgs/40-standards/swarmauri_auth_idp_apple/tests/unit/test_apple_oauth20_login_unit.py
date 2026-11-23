import json

import pytest
from pydantic import SecretBytes

from swarmauri_auth_idp_apple import AppleOAuth20Login


@pytest.fixture
def login() -> AppleOAuth20Login:
    return AppleOAuth20Login(
        team_id="team",
        key_id="key",
        client_id="client",
        private_key_pem=SecretBytes(b"dummy"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"state-secret"),
    )


@pytest.mark.unit
def test_resource(login: AppleOAuth20Login) -> None:
    assert login.resource == "OAuth20Login"


@pytest.mark.unit
def test_type(login: AppleOAuth20Login) -> None:
    assert login.type == "AppleOAuth20Login"


@pytest.mark.unit
def test_initialization(login: AppleOAuth20Login) -> None:
    assert isinstance(login.id, str)


@pytest.mark.unit
def test_serialization(login: AppleOAuth20Login) -> None:
    serialized = login.model_dump_json()
    data = json.loads(serialized)

    restored = AppleOAuth20Login.model_construct(**data)
    restored.private_key_pem = login.private_key_pem
    restored.state_secret = login.state_secret

    assert restored.id == login.id
    assert restored.resource == login.resource
    assert restored.type == login.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_includes_pkce(login: AppleOAuth20Login) -> None:
    payload = await login.auth_url()
    assert "url" in payload
    assert "state" in payload
    assert "code_challenge_method=S256" in payload["url"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_invalid_state(login: AppleOAuth20Login) -> None:
    with pytest.raises(ValueError):
        await login.exchange_and_identity("code", "invalid-state")
