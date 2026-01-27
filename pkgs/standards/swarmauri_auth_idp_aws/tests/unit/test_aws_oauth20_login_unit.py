import json

import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_aws import AwsOAuth20Login


@pytest.fixture
def login() -> AwsOAuth20Login:
    return AwsOAuth20Login(
        authorization_endpoint="https://example.awsapps.com/start/oauth2/authorize",
        token_endpoint="https://example.awsapps.com/start/oauth2/token",
        client_id="client-id",
        client_secret=SecretStr("client-secret"),
        redirect_uri="https://app.example.com/callback",
        state_secret=b"state-secret",
    )


@pytest.mark.unit
def test_resource(login: AwsOAuth20Login) -> None:
    assert login.resource == "OAuth20Login"


@pytest.mark.unit
def test_type(login: AwsOAuth20Login) -> None:
    assert login.type == "AwsOAuth20Login"


@pytest.mark.unit
def test_initialization(login: AwsOAuth20Login) -> None:
    assert isinstance(login.id, str)


@pytest.mark.unit
def test_serialization(login: AwsOAuth20Login) -> None:
    serialized = login.model_dump_json()
    data = json.loads(serialized)

    restored = AwsOAuth20Login.model_construct(**data)
    restored.client_secret = login.client_secret

    assert restored.id == login.id
    assert restored.resource == login.resource
    assert restored.type == login.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_contains_pkce(login: AwsOAuth20Login) -> None:
    payload = await login.auth_url()
    assert "code_challenge_method=S256" in payload["url"]
    assert payload["state"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_and_identity_returns_tokens(
    login: AwsOAuth20Login, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def fake_post_token(form):
        assert form["code"] == "auth-code"
        return {"access_token": "atk"}

    monkeypatch.setattr(login, "_post_token", fake_post_token)

    auth = await login.auth_url()
    result = await login.exchange_and_identity("auth-code", auth["state"])
    assert result == {"issuer": "aws-workforce", "tokens": {"access_token": "atk"}}
