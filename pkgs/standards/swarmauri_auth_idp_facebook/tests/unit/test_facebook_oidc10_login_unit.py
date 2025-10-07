import json

import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_facebook import FacebookOIDC10Login


@pytest.fixture
def login() -> FacebookOIDC10Login:
    return FacebookOIDC10Login(
        client_id="app-id",
        client_secret=SecretStr("app-secret"),
        redirect_uri="https://app.example.com/callback",
        state_secret=b"state-secret",
    )


@pytest.mark.unit
def test_resource(login: FacebookOIDC10Login) -> None:
    assert login.resource == "OIDC10Login"


@pytest.mark.unit
def test_type(login: FacebookOIDC10Login) -> None:
    assert login.type == "FacebookOIDC10Login"


@pytest.mark.unit
def test_serialization(login: FacebookOIDC10Login) -> None:
    data = json.loads(login.model_dump_json())
    restored = FacebookOIDC10Login.model_construct(**data)
    restored.client_secret = login.client_secret
    assert restored.id == login.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_contains_pkce(
    login: FacebookOIDC10Login, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def fake_metadata():
        return {
            "authorization_endpoint": "https://www.facebook.com/v19.0/dialog/oauth",
            "token_endpoint": "https://graph.facebook.com/oauth/access_token",
            "jwks_uri": "https://www.facebook.com/.well-known/oauth/openid/jwks/",
            "issuer": "https://www.facebook.com",
        }

    monkeypatch.setattr(login, "_metadata", fake_metadata)

    payload = await login.auth_url()
    assert "code_challenge_method=S256" in payload["url"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_returns_claims(
    login: FacebookOIDC10Login, monkeypatch: pytest.MonkeyPatch
) -> None:
    metadata = {
        "authorization_endpoint": "https://www.facebook.com/v19.0/dialog/oauth",
        "token_endpoint": "https://graph.facebook.com/oauth/access_token",
        "jwks_uri": "https://www.facebook.com/.well-known/oauth/openid/jwks/",
        "issuer": "https://www.facebook.com",
    }

    async def fake_metadata():
        return metadata

    async def fake_token_request(endpoint: str, form):
        assert endpoint == metadata["token_endpoint"]
        assert form["code"] == "auth-code"
        return {"id_token": "encoded", "access_token": "atk"}

    async def fake_jwks(url: str):
        assert url == metadata["jwks_uri"]
        return {"keys": []}

    def fake_decode_id_token(id_token: str, *, jwks, issuer):
        assert id_token == "encoded"
        return {"sub": "user-id", "email": "user@example.com", "name": "Example"}

    monkeypatch.setattr(login, "_metadata", fake_metadata)
    monkeypatch.setattr(login, "_token_request", fake_token_request)
    monkeypatch.setattr(login, "_jwks", fake_jwks)
    monkeypatch.setattr(login, "_decode_id_token", fake_decode_id_token)

    payload = await login.auth_url()
    result = await login.exchange("auth-code", payload["state"])
    assert result["issuer"] == "facebook-oidc10"
    assert result["sub"] == "user-id"
    assert result["email"] == "user@example.com"
