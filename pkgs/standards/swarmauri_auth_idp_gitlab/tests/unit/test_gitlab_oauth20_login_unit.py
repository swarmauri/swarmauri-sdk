import json

import pytest
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_gitlab import GitLabOAuth20Login


@pytest.fixture
def login() -> GitLabOAuth20Login:
    return GitLabOAuth20Login(
        base_url="https://gitlab.example",
        client_id="client",
        client_secret=SecretStr("secret"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"state-secret"),
    )


@pytest.mark.unit
def test_resource(login: GitLabOAuth20Login) -> None:
    assert login.resource == "OAuth20Login"


@pytest.mark.unit
def test_type(login: GitLabOAuth20Login) -> None:
    assert login.type == "GitLabOAuth20Login"


@pytest.mark.unit
def test_serialization(login: GitLabOAuth20Login) -> None:
    serialized = login.model_dump_json()
    payload = json.loads(serialized)

    restored = GitLabOAuth20Login.model_construct(**payload)
    restored.client_secret = login.client_secret
    restored.state_secret = login.state_secret

    assert restored.id == login.id
    assert restored.resource == login.resource
    assert restored.type == login.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_contains_gitlab(login: GitLabOAuth20Login) -> None:
    payload = await login.auth_url()
    assert payload["url"].startswith("https://gitlab.example/oauth/authorize?")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_invalid_state(login: GitLabOAuth20Login) -> None:
    with pytest.raises(ValueError):
        await login.exchange_and_identity("code", "invalid-state")
