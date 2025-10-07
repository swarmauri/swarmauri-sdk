import json

import pytest
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_gitea import GiteaOAuth21Login


@pytest.fixture
def login() -> GiteaOAuth21Login:
    return GiteaOAuth21Login(
        base_url="https://gitea.example",
        client_id="client",
        client_secret=SecretStr("secret"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"state-secret"),
    )


@pytest.mark.unit
def test_resource(login: GiteaOAuth21Login) -> None:
    assert login.resource == "OAuth21Login"


@pytest.mark.unit
def test_type(login: GiteaOAuth21Login) -> None:
    assert login.type == "GiteaOAuth21Login"


@pytest.mark.unit
def test_serialization(login: GiteaOAuth21Login) -> None:
    serialized = login.model_dump_json()
    data = json.loads(serialized)

    restored = GiteaOAuth21Login.model_construct(**data)
    restored.client_secret = login.client_secret
    restored.state_secret = login.state_secret

    assert restored.id == login.id
    assert restored.resource == login.resource
    assert restored.type == login.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_uses_base_url(login: GiteaOAuth21Login) -> None:
    payload = await login.auth_url()
    assert payload["url"].startswith("https://gitea.example/login/oauth/authorize?")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_invalid_state(login: GiteaOAuth21Login) -> None:
    with pytest.raises(ValueError):
        await login.exchange_and_identity("code", "invalid-state")
