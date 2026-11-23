"""Exercise Azure OAuth exchange using a fresh login's default HTTP client."""

import httpx
import pytest
from pydantic import SecretStr
from swarmauri_base.auth_idp.http import RetryingAsyncClient

from swarmauri_auth_idp_azure import AzureOAuth20Login, AzureOAuth21Login


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("login_class", [AzureOAuth20Login, AzureOAuth21Login])
async def test_fresh_login_exchanges_code_and_fetches_profile(
    login_class, monkeypatch
):
    token_url = "https://login.microsoftonline.com/tenant/oauth2/v2.0/token"
    profile_url = "https://graph.microsoft.com/v1.0/me"

    async def post(client, url, **kwargs):
        assert url == token_url
        return httpx.Response(
            200,
            request=httpx.Request("POST", url),
            json={"access_token": "test-token"},
        )

    async def get(client, url, **kwargs):
        assert url == profile_url
        assert kwargs["headers"]["Authorization"] == "Bearer test-token"
        return httpx.Response(
            200,
            request=httpx.Request("GET", url),
            json={"id": "user-id", "mail": "user@example.com"},
        )

    monkeypatch.setattr(RetryingAsyncClient, "post", post)
    monkeypatch.setattr(RetryingAsyncClient, "get", get)

    login = login_class(
        tenant="tenant",
        client_id="client-id",
        client_secret=SecretStr("client-secret"),
        redirect_uri="https://example.com/callback",
        state_secret=b"state-secret",
    )
    auth = await login.auth_url()
    identity = await login.exchange_and_identity("auth-code", auth["state"])

    assert identity["sub"] == "user-id"
    assert identity["email"] == "user@example.com"
