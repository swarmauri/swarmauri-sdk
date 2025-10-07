import json

import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_azure import AzureOIDC10Login


@pytest.fixture
def login() -> AzureOIDC10Login:
    return AzureOIDC10Login(
        tenant="organizations",
        client_id="client-id",
        client_secret=SecretStr("client-secret"),
        redirect_uri="https://app.example.com/callback",
        state_secret=b"state-secret",
    )


@pytest.mark.unit
def test_resource(login: AzureOIDC10Login) -> None:
    assert login.resource == "OIDC10Login"


@pytest.mark.unit
def test_type(login: AzureOIDC10Login) -> None:
    assert login.type == "AzureOIDC10Login"


@pytest.mark.unit
def test_serialization(login: AzureOIDC10Login) -> None:
    data = json.loads(login.model_dump_json())
    clone = AzureOIDC10Login.model_construct(**data)
    clone.client_secret = login.client_secret
    assert clone.id == login.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_contains_pkce(
    login: AzureOIDC10Login, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def fake_metadata():
        return {
            "authorization_endpoint": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            "token_endpoint": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            "jwks_uri": "https://login.microsoftonline.com/common/discovery/v2.0/keys",
            "issuer": "https://login.microsoftonline.com/{tenantid}/v2.0",
        }

    monkeypatch.setattr(login, "_metadata", fake_metadata)

    payload = await login.auth_url()
    assert "code_challenge_method=S256" in payload["url"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_returns_claims(
    login: AzureOIDC10Login, monkeypatch: pytest.MonkeyPatch
) -> None:
    metadata = {
        "authorization_endpoint": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "token_endpoint": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "jwks_uri": "https://login.microsoftonline.com/common/discovery/v2.0/keys",
        "issuer": "https://login.microsoftonline.com/{tenantid}/v2.0",
    }

    async def fake_metadata():
        return metadata

    async def fake_token_request(endpoint, form):
        assert endpoint == metadata["token_endpoint"]
        assert form["code"] == "auth-code"
        assert form["client_id"] == "client-id"
        assert form["client_secret"] == "client-secret"
        return {"id_token": "encoded"}

    async def fake_jwks(url):
        assert url == metadata["jwks_uri"]
        return {"keys": []}

    def fake_decode(id_token, *, jwks, expected_issuer):
        assert id_token == "encoded"
        assert expected_issuer == metadata["issuer"]
        assert jwks == {"keys": []}
        return {
            "sub": "user-id",
            "email": "user@example.com",
            "name": "Example User",
        }

    monkeypatch.setattr(login, "_metadata", fake_metadata)
    monkeypatch.setattr(login, "_token_request", fake_token_request)
    monkeypatch.setattr(login, "_jwks", fake_jwks)
    monkeypatch.setattr(login, "_decode_id_token", fake_decode)

    payload = await login.auth_url()
    result = await login.exchange("auth-code", payload["state"])
    assert result["issuer"] == "azure-oidc10"
    assert result["claims"]["sub"] == "user-id"
    assert result["email"] == "user@example.com"
    assert result["name"] == "Example User"
