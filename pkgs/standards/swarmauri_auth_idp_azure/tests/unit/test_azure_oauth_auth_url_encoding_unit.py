"""Regression tests for authorization-URL query encoding (#6277).

Before the fix, ``_auth_payload`` (and the OIDC ``auth_url``) interpolated
the query values straight into the authorization URL, so reserved characters
inside a value could break out of its own parameter. These tests parse the
resulting query and round-trip values containing ``&``, ``+``, ``=``, spaces,
and Unicode, including a redirect URI that carries its own query string.
"""

from urllib.parse import parse_qs, urlsplit

import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_azure import (
    AzureOAuth20Login,
    AzureOAuth21Login,
    AzureOIDC10Login,
)

# Values chosen so that, unencoded, each would break out of its own
# query parameter: "&" would split a parameter, "+" reads as a space,
# and the scope carries an apparent extra parameter plus Unicode.
TRICKY_CLIENT_ID = "client&state=evil+id"
TRICKY_REDIRECT_URI = "https://example.com/callback?next=/home&tab=1"
TRICKY_SCOPE = "openid email&code_challenge_method=none ünïcode"

BASE_PARAMS = {
    "response_type",
    "client_id",
    "redirect_uri",
    "scope",
    "state",
    "code_challenge",
    "code_challenge_method",
}

AUTH_ENDPOINT = "https://login.microsoftonline.com/organizations/oauth2/v2.0/authorize"


def _login(cls):
    return cls(
        tenant="organizations",
        client_id=TRICKY_CLIENT_ID,
        client_secret=SecretStr("client-secret"),
        redirect_uri=TRICKY_REDIRECT_URI,
        state_secret=b"state-secret",
        scope=TRICKY_SCOPE,
    )


def _assert_round_trips(url: str, state: str, expected_params) -> None:
    assert url.startswith(f"{AUTH_ENDPOINT}?")
    parsed = parse_qs(urlsplit(url).query)

    # No value may introduce a second top-level parameter.
    assert set(parsed) == expected_params
    assert parsed["client_id"] == [TRICKY_CLIENT_ID]
    assert parsed["redirect_uri"] == [TRICKY_REDIRECT_URI]
    assert parsed["scope"] == [TRICKY_SCOPE]
    # The apparent extra parameters inside the values stay inside them:
    # the real state survives and S256 is not replaced.
    assert parsed["state"] == [state]
    assert parsed["code_challenge_method"] == ["S256"]
    assert parsed["response_type"] == ["code"]
    assert len(parsed["code_challenge"]) == 1
    assert parsed["code_challenge"][0]


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("cls", [AzureOAuth20Login, AzureOAuth21Login])
async def test_auth_url_encodes_reserved_characters(cls) -> None:
    login = _login(cls)
    payload = await login.auth_url()

    expected_params = set(BASE_PARAMS)
    if cls is AzureOAuth21Login:
        expected_params |= {"prompt"}
    _assert_round_trips(payload["url"], payload["state"], expected_params)

    if cls is AzureOAuth21Login:
        parsed = parse_qs(urlsplit(payload["url"]).query)
        assert parsed["prompt"] == ["select_account"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_auth_url_encodes_reserved_characters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    login = _login(AzureOIDC10Login)

    async def fake_metadata():
        return {
            "authorization_endpoint": AUTH_ENDPOINT,
            "token_endpoint": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            "jwks_uri": "https://login.microsoftonline.com/common/discovery/v2.0/keys",
            "issuer": "https://login.microsoftonline.com/{tenantid}/v2.0",
        }

    monkeypatch.setattr(login, "_metadata", fake_metadata)

    payload = await login.auth_url()
    _assert_round_trips(payload["url"], payload["state"], set(BASE_PARAMS))


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_auth_url_preserves_endpoint_query(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    login = _login(AzureOIDC10Login)

    async def fake_metadata():
        return {
            "authorization_endpoint": f"{AUTH_ENDPOINT}?foo=bar",
            "token_endpoint": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            "jwks_uri": "https://login.microsoftonline.com/common/discovery/v2.0/keys",
            "issuer": "https://login.microsoftonline.com/{tenantid}/v2.0",
        }

    monkeypatch.setattr(login, "_metadata", fake_metadata)

    payload = await login.auth_url()
    parsed = parse_qs(urlsplit(payload["url"]).query)

    assert parsed["foo"] == ["bar"]
    assert set(parsed) == BASE_PARAMS | {"foo"}
    assert parsed["redirect_uri"] == [TRICKY_REDIRECT_URI]
    assert parsed["code_challenge_method"] == ["S256"]
