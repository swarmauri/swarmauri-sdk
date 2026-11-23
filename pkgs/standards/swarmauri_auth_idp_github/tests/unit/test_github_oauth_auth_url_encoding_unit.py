"""Regression tests for authorization-URL query encoding (#6285).

Before the fix, ``_auth_payload`` interpolated the query values straight
into the authorization URL, so reserved characters inside a value could
break out of its own parameter. These tests parse the resulting query and
round-trip values containing ``&``, ``+``, ``=``, spaces, and Unicode,
including a redirect URI that carries its own query string.
"""

from urllib.parse import parse_qs, urlsplit

import pytest
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_github import GitHubOAuth20Login, GitHubOAuth21Login

# Values chosen so that, unencoded, each would break out of its own
# query parameter: "&" would split a parameter, "+" reads as a space,
# and the scope carries an apparent extra parameter plus Unicode.
TRICKY_CLIENT_ID = "client&state=evil+id"
TRICKY_REDIRECT_URI = "https://example.com/callback?next=/home&tab=1"
TRICKY_SCOPE = "openid email&code_challenge_method=none ünïcode"

EXPECTED_PARAMS = {
    "client_id",
    "redirect_uri",
    "scope",
    "state",
    "code_challenge",
    "code_challenge_method",
}


def _login(cls, **overrides):
    return cls(
        client_id=TRICKY_CLIENT_ID,
        client_secret=SecretStr("secret"),
        redirect_uri=TRICKY_REDIRECT_URI,
        state_secret=SecretBytes(b"signing-secret"),
        scope=TRICKY_SCOPE,
        **overrides,
    )


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("cls", [GitHubOAuth20Login, GitHubOAuth21Login])
async def test_auth_url_encodes_reserved_characters(cls) -> None:
    login = _login(cls)
    payload = await login.auth_url()
    assert payload["url"].startswith(
        "https://github.com/login/oauth/authorize?"
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
    assert len(parsed["code_challenge"]) == 1
    assert parsed["code_challenge"][0]


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("cls", [GitHubOAuth20Login, GitHubOAuth21Login])
async def test_auth_url_preserves_endpoint_query(cls) -> None:
    # GitHub builds its endpoint from oauth_base, which carries no query,
    # so the merge branch is exercised through an endpoint that does.
    class QueryEndpointLogin(cls):
        def _authorization_endpoint(self) -> str:
            return "https://github.example/login/oauth/authorize?foo=bar"

    login = _login(QueryEndpointLogin)
    payload = await login.auth_url()
    parsed = parse_qs(urlsplit(payload["url"]).query)

    assert parsed["foo"] == ["bar"]
    assert set(parsed) == EXPECTED_PARAMS | {"foo"}
    assert parsed["redirect_uri"] == [TRICKY_REDIRECT_URI]
    assert parsed["code_challenge_method"] == ["S256"]
