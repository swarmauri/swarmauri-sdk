import json

import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_aws import AwsOAuth21Login


@pytest.fixture
def login() -> AwsOAuth21Login:
    return AwsOAuth21Login(
        authorization_endpoint="https://example.awsapps.com/start/oauth2/authorize",
        token_endpoint="https://example.awsapps.com/start/oauth2/token",
        client_id="client-id",
        client_secret=SecretStr("client-secret"),
        redirect_uri="https://app.example.com/callback",
        state_secret=b"state-secret",
    )


@pytest.mark.unit
def test_resource(login: AwsOAuth21Login) -> None:
    assert login.resource == "OAuth21Login"


@pytest.mark.unit
def test_type(login: AwsOAuth21Login) -> None:
    assert login.type == "AwsOAuth21Login"


@pytest.mark.unit
def test_initialization(login: AwsOAuth21Login) -> None:
    assert isinstance(login.id, str)


@pytest.mark.unit
def test_serialization(login: AwsOAuth21Login) -> None:
    serialized = login.model_dump_json()
    data = json.loads(serialized)

    restored = AwsOAuth21Login.model_construct(**data)
    restored.client_secret = login.client_secret

    assert restored.id == login.id
    assert restored.resource == login.resource
    assert restored.type == login.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_includes_prompt(login: AwsOAuth21Login) -> None:
    payload = await login.auth_url()
    assert "prompt=consent" in payload["url"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_and_identity_returns_tokens(
    login: AwsOAuth21Login, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def fake_post_token(form):
        assert form["code"] == "auth-code"
        return {"access_token": "atk"}

    monkeypatch.setattr(login, "_post_token", fake_post_token)

    auth = await login.auth_url()
    result = await login.exchange_and_identity("auth-code", auth["state"])
    assert result["issuer"] == "aws-workforce"
    assert result["tokens"]["access_token"] == "atk"
