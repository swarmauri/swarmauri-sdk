"""Regression tests for authorization-URL query encoding (#6294).

Before the fix, ``_auth_payload`` interpolated the query values straight
into the authorization URL, so reserved characters inside a value could
break out of its own parameter. These tests parse the resulting query and
round-trip values containing ``&``, ``+``, ``=``, spaces, and Unicode,
including a redirect URI that carries its own query string.
"""

from urllib.parse import parse_qs, urlsplit

import pytest
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_okta import (
    OktaOAuth20Login,
    OktaOAuth21Login,
    OktaOIDC10Login,
)

# Values chosen so that, unencoded, each would break out of its own
# query parameter: "&" would split a parameter, "+" reads as a space,
# and the scope carries an apparent extra parameter plus Unicode.
TRICKY_CLIENT_ID = "client&state=evil+id"
TRICKY_REDIRECT_URI = "https://example.com/callback?next=/home&tab=1"
TRICKY_SCOPE = "openid email&code_challenge_method=none ünïcode"

EXPECTED_PARAMS = {
    "response_type",
    "client_id",
    "redirect_uri",
    "scope",
    "state",
    "code_challenge",
    "code_challenge_method",
    "prompt",
}


def _login(cls, endpoint):
    instance = cls(
        issuer="https://okta.example/oauth2/default",
        client_id=TRICKY_CLIENT_ID,
        client_secret=SecretStr("secret"),
        redirect_uri=TRICKY_REDIRECT_URI,
        state_secret=SecretBytes(b"state-secret"),
        scope=TRICKY_SCOPE,
    )
    instance.discovery_cache = {
        "authorization_endpoint": endpoint,
        "token_endpoint": "https://okta.example/oauth2/default/v1/token",
        "userinfo_endpoint": "https://okta.example/oauth2/default/v1/userinfo",
        "jwks_uri": "https://okta.example/oauth2/default/v1/keys",
    }
    return instance


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("cls", [OktaOAuth20Login, OktaOAuth21Login])
async def test_auth_url_encodes_reserved_characters(cls) -> None:
    login = _login(cls, "https://okta.example/oauth2/default/v1/authorize")
    payload = await login.auth_url()
    assert payload["url"].startswith(
        "https://okta.example/oauth2/default/v1/authorize?"
    )
    parsed = parse_qs(urlsplit(payload["url"]).query)

    # No value may introduce a second top-level parameter.
    assert set(parsed) == EXPECTED_PARAMS
    assert parsed["client_id"] == [TRICKY_CLIENT_ID]
    assert parsed["redirect_uri"] == [TRICKY_REDIRECT_URI]
    assert parsed["scope"] == [TRICKY_SCOPE]
    # The apparent extra parameters inside the values stay inside them:
    # the real state survives and S256 is not replaced.
    assert parsed["state"] == [payload["state"]]
    assert parsed["code_challenge_method"] == ["S256"]
    assert parsed["response_type"] == ["code"]
    assert parsed["prompt"] == ["consent"]
    assert len(parsed["code_challenge"]) == 1
    assert parsed["code_challenge"][0]


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "cls", [OktaOAuth20Login, OktaOAuth21Login, OktaOIDC10Login]
)
async def test_auth_url_replaces_generated_endpoint_parameters(cls) -> None:
    login = _login(
        cls,
        "https://okta.example/oauth2/default/v1/authorize"
        "?foo=bar&foo=&st%61te=old&code_challenge_method=plain",
    )
    payload = await login.auth_url()
    parsed = parse_qs(urlsplit(payload["url"]).query, keep_blank_values=True)

    assert parsed["foo"] == ["bar", ""]
    assert set(parsed) == EXPECTED_PARAMS | {"foo"}
    assert parsed["redirect_uri"] == [TRICKY_REDIRECT_URI]
    assert parsed["state"] == [payload["state"]]
    assert parsed["code_challenge_method"] == ["S256"]
