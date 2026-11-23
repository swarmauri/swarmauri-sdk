"""Regression tests for authorization-URL query encoding (#6287).

Before the fix, ``_auth_payload`` interpolated the query values straight
into the authorization URL, so reserved characters inside a value could
break out of its own parameter. These tests parse the resulting query and
round-trip values containing ``&``, ``+``, ``=``, spaces, and Unicode,
including a redirect URI that carries its own query string.
"""

from urllib.parse import parse_qs, urlsplit

import pytest
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_gitlab import (
    GitLabOAuth20Login,
    GitLabOAuth21Login,
    GitLabOIDC10Login,
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
}

DISCOVERY = {
    "authorization_endpoint": "https://gitlab.example/oauth/authorize",
    "token_endpoint": "https://gitlab.example/oauth/token",
    "jwks_uri": "https://gitlab.example/oauth/jwks",
}


def _login(cls, endpoint=None):
    if cls is GitLabOAuth20Login:
        return cls(
            base_url="https://gitlab.example",
            client_id=TRICKY_CLIENT_ID,
            client_secret=SecretStr("secret"),
            redirect_uri=TRICKY_REDIRECT_URI,
            state_secret=SecretBytes(b"state-secret"),
            scope=TRICKY_SCOPE,
        )
    instance = cls(
        issuer="https://gitlab.example",
        client_id=TRICKY_CLIENT_ID,
        client_secret=SecretStr("secret"),
        redirect_uri=TRICKY_REDIRECT_URI,
        state_secret=SecretBytes(b"state-secret"),
        scope=TRICKY_SCOPE,
    )
    instance.discovery_cache = {
        **DISCOVERY,
        "authorization_endpoint": endpoint
        or "https://gitlab.example/oauth/authorize",
    }
    return instance


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "cls", [GitLabOAuth20Login, GitLabOAuth21Login, GitLabOIDC10Login]
)
async def test_auth_url_encodes_reserved_characters(cls) -> None:
    login = _login(cls)
    payload = await login.auth_url()
    assert payload["url"].startswith("https://gitlab.example/oauth/authorize?")
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
    "cls", [GitLabOAuth20Login, GitLabOAuth21Login, GitLabOIDC10Login]
)
async def test_auth_url_replaces_generated_endpoint_parameters(
    cls, monkeypatch: pytest.MonkeyPatch
) -> None:
    endpoint = (
        "https://gitlab.example/oauth/authorize"
        "?foo=bar&foo=&st%61te=stale&code_challenge_method=plain"
    )
    login = _login(cls, endpoint)
    if cls is GitLabOAuth20Login:
        monkeypatch.setattr(
            cls, "_authorization_endpoint", lambda self: endpoint
        )
    payload = await login.auth_url()
    parsed = parse_qs(urlsplit(payload["url"]).query, keep_blank_values=True)

    assert parsed["foo"] == ["bar", ""]
    assert set(parsed) == EXPECTED_PARAMS | {"foo"}
    assert parsed["redirect_uri"] == [TRICKY_REDIRECT_URI]
    assert parsed["state"] == [payload["state"]]
    assert parsed["code_challenge_method"] == ["S256"]
