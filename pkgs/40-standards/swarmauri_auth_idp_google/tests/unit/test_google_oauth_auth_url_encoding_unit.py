"""Regression tests for authorization-URL query encoding (#6289).

Before the fix, ``_auth_payload`` in both Google login mixins interpolated
the query values straight into the authorization URL, so reserved characters
inside a value could break out of its own parameter. These tests parse the
resulting query and round-trip values containing ``&``, ``+``, ``=``, spaces,
and Unicode, including a redirect URI that carries its own query string.
"""

from urllib.parse import parse_qs, urlsplit

import pytest
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_google import (
    GoogleOAuth20Login,
    GoogleOAuth21Login,
    GoogleOIDC10Login,
)

# Values chosen so that, unencoded, each would break out of its own
# query parameter: "&" would split a parameter, "+" reads as a space,
# and the scope carries an apparent extra parameter plus Unicode.
TRICKY_CLIENT_ID = "client&state=evil+id"
TRICKY_REDIRECT_URI = "https://example.com/callback?next=/home&tab=1"
TRICKY_SCOPE = "openid email&code_challenge_method=none ünïcode"

OAUTH_PARAMS = {
    "response_type",
    "client_id",
    "redirect_uri",
    "scope",
    "state",
    "code_challenge",
    "code_challenge_method",
    "access_type",
    "prompt",
}

OIDC_PARAMS = {
    "response_type",
    "client_id",
    "redirect_uri",
    "scope",
    "state",
    "nonce",
    "code_challenge",
    "code_challenge_method",
    "include_granted_scopes",
    "prompt",
}

GOOGLE_AUTHORIZE = "https://accounts.google.com/o/oauth2/v2/auth"


def _login(cls, endpoint=None):
    instance = cls(
        client_id=TRICKY_CLIENT_ID,
        client_secret=SecretStr("secret"),
        redirect_uri=TRICKY_REDIRECT_URI,
        state_secret=SecretBytes(b"state-secret"),
        scope=TRICKY_SCOPE,
    )
    if endpoint is not None:
        instance.discovery_cache = {
            "authorization_endpoint": endpoint,
            "token_endpoint": "https://google.example/oauth2/v4/token",
            "jwks_uri": "https://google.example/.well-known/jwks.json",
            "issuer": "https://accounts.google.com",
        }
    return instance


def _assert_round_trip(parsed, payload, expected_params):
    # No value may introduce a second top-level parameter.
    assert set(parsed) == expected_params
    assert parsed["client_id"] == [TRICKY_CLIENT_ID]
    assert parsed["redirect_uri"] == [TRICKY_REDIRECT_URI]
    assert parsed["scope"] == [TRICKY_SCOPE]
    # The apparent extra parameters inside the values stay inside them:
    # the real state survives and S256 is not replaced.
    assert parsed["state"] == [payload["state"]]
    assert parsed["code_challenge_method"] == ["S256"]
    assert parsed["response_type"] == ["code"]
    assert parsed["prompt"] == ["select_account"]
    assert len(parsed["code_challenge"]) == 1
    assert parsed["code_challenge"][0]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_encodes_reserved_characters_oauth20() -> None:
    login = _login(GoogleOAuth20Login)
    payload = await login.auth_url()
    assert payload["url"].startswith(GOOGLE_AUTHORIZE + "?")
    parsed = parse_qs(urlsplit(payload["url"]).query)

    _assert_round_trip(parsed, payload, OAUTH_PARAMS)
    assert parsed["access_type"] == ["offline"]


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("cls", [GoogleOAuth21Login, GoogleOIDC10Login])
async def test_auth_url_encodes_reserved_characters_oidc(cls) -> None:
    login = _login(cls, GOOGLE_AUTHORIZE)
    payload = await login.auth_url()
    assert payload["url"].startswith(GOOGLE_AUTHORIZE + "?")
    parsed = parse_qs(urlsplit(payload["url"]).query)

    _assert_round_trip(parsed, payload, OIDC_PARAMS)
    assert parsed["include_granted_scopes"] == ["true"]
    assert len(parsed["nonce"]) == 1
    assert parsed["nonce"][0]


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("cls", [GoogleOAuth21Login, GoogleOIDC10Login])
async def test_auth_url_preserves_endpoint_query(cls) -> None:
    login = _login(cls, GOOGLE_AUTHORIZE + "?foo=bar")
    payload = await login.auth_url()
    parsed = parse_qs(urlsplit(payload["url"]).query)

    assert parsed["foo"] == ["bar"]
    assert set(parsed) == OIDC_PARAMS | {"foo"}
    assert parsed["redirect_uri"] == [TRICKY_REDIRECT_URI]
    assert parsed["code_challenge_method"] == ["S256"]
