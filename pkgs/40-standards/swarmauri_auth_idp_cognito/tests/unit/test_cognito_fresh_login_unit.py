"""Exercise Cognito discovery through fresh login instances."""

import httpx
import pytest
from pydantic import SecretBytes, SecretStr
from swarmauri_base.auth_idp.http import RetryingAsyncClient

from swarmauri_auth_idp_cognito import (
    CognitoOAuth20Login,
    CognitoOAuth21Login,
    CognitoOIDC10Login,
)


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "login_class",
    [CognitoOAuth20Login, CognitoOAuth21Login, CognitoOIDC10Login],
)
async def test_fresh_logins_discover_and_cache_metadata_per_instance(
    login_class, monkeypatch
):
    issuer = "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_pool"
    authorization_url = "https://pool.example.com/oauth2/authorize"
    discovery_url = f"{issuer}/.well-known/openid-configuration"
    discovery_requests = []

    async def get(client, url, **kwargs):
        discovery_requests.append(url)
        return httpx.Response(
            200,
            request=httpx.Request("GET", url),
            json={"authorization_endpoint": authorization_url},
        )

    monkeypatch.setattr(RetryingAsyncClient, "get", get)
    fields = {
        "issuer": issuer,
        "client_id": "client-id",
        "client_secret": SecretStr("client-secret"),
        "redirect_uri": "https://example.com/callback",
        "state_secret": SecretBytes(b"state-secret"),
    }
    first = login_class(**fields)

    for _ in range(2):
        auth = await first.auth_url()
        assert auth["url"].split("?", 1)[0] == authorization_url
    assert discovery_requests == [discovery_url]

    second = login_class(**fields)
    auth = await second.auth_url()
    assert auth["url"].split("?", 1)[0] == authorization_url
    assert discovery_requests == [discovery_url, discovery_url]
