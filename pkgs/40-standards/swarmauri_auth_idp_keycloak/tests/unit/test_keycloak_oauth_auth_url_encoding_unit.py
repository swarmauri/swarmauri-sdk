"""Regression tests for authorization-URL query encoding (#6291).

Before the fix, ``_auth_payload`` interpolated the query values straight
into the authorization URL, so reserved characters inside a value could
break out of its own parameter. These tests parse the resulting query and
round-trip values containing ``&``, ``+``, ``=``, spaces, and Unicode,
including a redirect URI that carries its own query string.
"""

from urllib.parse import parse_qs, urlsplit

import pytest
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_keycloak import (
    KeycloakOAuth20Login,
    KeycloakOAuth21Login,
    KeycloakOIDC10Login,
)

# Values chosen so that, unencoded, each would break out of its own
# query parameter: "&" would split a parameter, "+" reads as a space,
# and the scope carries an apparent extra parameter plus Unicode.
TRICKY_CLIENT_ID = "client&state=evil+id"
TRICKY_REDIRECT_URI = "https://example.com/callback?next=/home&tab=1"
TRICKY_SCOPE = "openid email&code_challenge_method=none \u00fcn\u00efcode"

EXPECTED_PARAMS = {
    "response_type",
    "client_id",
    "redirect_uri",
    "scope",
    "state",
    "code_challenge",
    "code_challenge_method",
}

AUTH_ENDPOINT = (
    "https://kc.example/realms/myrealm/protocol/openid-connect/auth"
)


def _login(cls, endpoint):
    instance = cls(
        issuer="https://kc.example/realms/myrealm",
        client_id=TRICKY_CLIENT_ID,
        client_secret=SecretStr("secret"),
        redirect_uri=TRICKY_REDIRECT_URI,
        state_secret=SecretBytes(b"0123456789abcdef0123456789abcdef"),
        scope=TRICKY_SCOPE,
    )
    instance.discovery_cache = {
        "authorization_endpoint": endpoint,
        "token_endpoint": "https://kc.example/realms/myrealm/protocol/openid-connect/token",
        "userinfo_endpoint": "https://kc.example/realms/myrealm/protocol/openid-connect/userinfo",
        "jwks_uri": "https://kc.example/realms/myrealm/protocol/openid-connect/certs",
    }
    return instance


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "cls", [KeycloakOAuth20Login, KeycloakOAuth21Login, KeycloakOIDC10Login]
)
async def test_auth_url_encodes_reserved_characters(cls) -> None:
    login = _login(cls, AUTH_ENDPOINT)
    payload = await login.auth_url()
    assert payload["url"].startswith(f"{AUTH_ENDPOINT}?")
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
    assert len(parsed["code_challenge"]) == 1
    assert parsed["code_challenge"][0]


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "cls", [KeycloakOAuth20Login, KeycloakOAuth21Login, KeycloakOIDC10Login]
)
async def test_auth_url_preserves_endpoint_query(cls) -> None:
    login = _login(cls, f"{AUTH_ENDPOINT}?foo=bar")
    payload = await login.auth_url()
    parsed = parse_qs(urlsplit(payload["url"]).query)

    assert parsed["foo"] == ["bar"]
    assert set(parsed) == EXPECTED_PARAMS | {"foo"}
    assert parsed["redirect_uri"] == [TRICKY_REDIRECT_URI]
    assert parsed["code_challenge_method"] == ["S256"]
