"""Regression tests for authorization-URL query encoding (#6281).

Before the fix, ``_auth_payload`` interpolated the query values straight
into the authorization URL, so reserved characters inside a value could
break out of its own parameter. These tests parse the resulting query and
round-trip values containing ``&``, ``+``, ``=``, spaces, and Unicode,
including a redirect URI that carries its own query string.
"""

from urllib.parse import parse_qs, urlsplit

import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_facebook import (
    FacebookOAuth20Login,
    FacebookOAuth21Login,
)

# Values chosen so that, unencoded, each would break out of its own
# query parameter: "&" would split a parameter, "+" reads as a space,
# and the scope carries an apparent extra parameter plus Unicode.
TRICKY_CLIENT_ID = "client&state=evil+id"
TRICKY_REDIRECT_URI = "https://example.com/callback?next=/home&tab=1"
TRICKY_SCOPE = "email public_profile&code_challenge_method=none ünïcode"

EXPECTED_PARAMS = {
    "response_type",
    "client_id",
    "redirect_uri",
    "scope",
    "state",
    "code_challenge",
    "code_challenge_method",
}


def _login(cls):
    return cls(
        client_id=TRICKY_CLIENT_ID,
        client_secret=SecretStr("app-secret"),
        redirect_uri=TRICKY_REDIRECT_URI,
        state_secret=b"state-secret",
        scope=TRICKY_SCOPE,
    )


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("cls", [FacebookOAuth20Login, FacebookOAuth21Login])
async def test_auth_url_encodes_reserved_characters(cls) -> None:
    login = _login(cls)
    payload = await login.auth_url()
    assert payload["url"].startswith(
        "https://www.facebook.com/v19.0/dialog/oauth?"
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
    assert len(parsed["code_challenge"]) == 1
    assert parsed["code_challenge"][0]


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("cls", [FacebookOAuth20Login, FacebookOAuth21Login])
async def test_auth_url_rejects_parameter_injection(cls) -> None:
    login = _login(cls)
    payload = await login.auth_url()
    url = payload["url"]

    # None of the apparent extra parameters inside the values may appear
    # as a raw top-level parameter in the URL.
    assert "&state=evil" not in url
    assert "code_challenge_method=none" not in url
    assert "tab=1" not in url
