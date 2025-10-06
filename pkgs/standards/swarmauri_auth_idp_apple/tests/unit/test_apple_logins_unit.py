import pytest

from swarmauri_auth_idp_apple import (
    AppleOAuth20AppClient,
    AppleOAuth20Login,
    AppleOAuth21Login,
    AppleOIDC10Login,
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_auth_url_includes_pkce() -> None:
    login = AppleOAuth20Login(
        team_id="team",
        key_id="key",
        client_id="client",
        private_key_pem=b"dummy",
        redirect_uri="https://example.com/callback",
        state_secret=b"state-secret",
    )
    payload = await login.auth_url()
    assert "url" in payload
    assert "state" in payload
    assert "code_challenge_method=S256" in payload["url"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_invalid_state_raises() -> None:
    login = AppleOAuth20Login(
        team_id="team",
        key_id="key",
        client_id="client",
        private_key_pem=b"dummy",
        redirect_uri="https://example.com/callback",
        state_secret=b"state-secret",
    )
    with pytest.raises(ValueError):
        await login.exchange_and_identity("code", "invalid-state")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_auth_url_uses_discovery() -> None:
    login = AppleOAuth21Login(
        team_id="team",
        key_id="key",
        client_id="client",
        private_key_pem=b"dummy",
        redirect_uri="https://example.com/callback",
        state_secret=b"state-secret",
    )
    login._discovery = {
        "authorization_endpoint": "https://apple.example/authorize",
        "token_endpoint": "https://apple.example/token",
        "jwks_uri": "https://apple.example/keys",
    }
    payload = await login.auth_url()
    assert payload["url"].startswith("https://apple.example/authorize?")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_exchange_invalid_state_fails() -> None:
    login = AppleOIDC10Login(
        team_id="team",
        key_id="key",
        client_id="client",
        private_key_pem=b"dummy",
        redirect_uri="https://example.com/callback",
        state_secret=b"state-secret",
    )
    login._discovery = {
        "authorization_endpoint": "https://apple.example/authorize",
        "token_endpoint": "https://apple.example/token",
        "jwks_uri": "https://apple.example/keys",
    }
    with pytest.raises(ValueError):
        await login.exchange("code", "invalid-state")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_app_client_unsupported() -> None:
    client = AppleOAuth20AppClient()
    with pytest.raises(NotImplementedError):
        await client.access_token()
