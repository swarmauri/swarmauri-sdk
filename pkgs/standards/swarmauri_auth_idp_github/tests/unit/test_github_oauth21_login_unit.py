import json

import pytest
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_github import GitHubOAuth21Login


@pytest.fixture
def login() -> GitHubOAuth21Login:
    return GitHubOAuth21Login(
        client_id="client",
        client_secret=SecretStr("secret"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"signing-secret"),
    )


@pytest.mark.unit
def test_resource(login: GitHubOAuth21Login) -> None:
    assert login.resource == "OAuth21Login"


@pytest.mark.unit
def test_type(login: GitHubOAuth21Login) -> None:
    assert login.type == "GitHubOAuth21Login"


@pytest.mark.unit
def test_serialization_round_trip(login: GitHubOAuth21Login) -> None:
    serialized = login.model_dump_json()
    payload = json.loads(serialized)

    restored = GitHubOAuth21Login.model_construct(**payload)
    restored.client_secret = login.client_secret
    restored.state_secret = login.state_secret

    assert restored.id == login.id
    assert restored.resource == login.resource
    assert restored.type == login.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_contains_github_base(login: GitHubOAuth21Login) -> None:
    payload = await login.auth_url()
    assert payload["url"].startswith("https://github.com/login/oauth/authorize?")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_invalid_state(login: GitHubOAuth21Login) -> None:
    with pytest.raises(ValueError):
        await login.exchange_and_identity("code", "invalid-state")
