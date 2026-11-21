"""Offline contract tests for the Cognito login flows (#6278).

Covers the primary public operation of each exported class, which the
existing unit tests only touch through construction, ``auth_url`` prefix
checks, and invalid-state failures:

- ``CognitoOAuth20Login.exchange_and_identity``: token exchange + UserInfo
  mapping (including the ``given_name``/``"Unknown"`` name fallbacks and
  the default ``oauth2/userInfo`` endpoint), and the token HTTP error and
  missing-``access_token`` failures.
- ``CognitoOAuth21Login.exchange_and_identity``: token exchange + ID token
  verification against a fake JWKS endpoint, name fallbacks, and the
  missing-``id_token`` / missing-``sub`` failures.
- ``CognitoOIDC10Login.exchange``: token exchange + ID token verification,
  with the UserInfo fallback only when the claims lack an email or a name,
  and the missing-``id_token`` failure.
- ``CognitoOAuth20AppClient.access_token``: client-credentials post
  (Basic auth, scope passthrough), token caching, and the
  missing-``access_token`` failure.
- ``CognitoOAuth21AppClient.access_token``: Basic-auth secret path and the
  JWT-bearer assertion path (assertion contents, 300s lifetime), and the
  missing-``access_token`` failure.
- ``CognitoOIDC10AppClient.access_token``: discovery through the fake
  client, token endpoint resolution, discovery reuse across calls, and
  the missing-``token_endpoint`` failure.

Everything runs offline: a fake HTTP client serves discovery metadata,
token responses, UserInfo, and JWKS, and the ID tokens and JWT assertions
are signed with a throwaway RSA key generated for these tests. No network
access, credentials, or live Cognito user pool are needed, and nothing
here proves interoperability with Cognito's production service.

Injection note: the fake client and discovery metadata are installed by
direct instance assignment (``login._http_client_factory = factory``,
``login._discovery = {...}``), the same approach the existing unit tests
already use for ``_discovery``. The constructor rejects the factory as an
extra input (``extra="forbid"``), and the mixin-declared private attributes
are not installed by pydantic (see the PR body: a fresh login instance
cannot run ``auth_url``/``exchange`` at all without this assignment).
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlsplit

import jwt
import pytest
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_cognito import (
    CognitoOAuth20AppClient,
    CognitoOAuth20Login,
    CognitoOAuth21AppClient,
    CognitoOAuth21Login,
    CognitoOIDC10AppClient,
    CognitoOIDC10Login,
)

ISSUER = "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_POOLID"
DOMAIN = "https://pool.auth.us-east-1.amazoncognito.com"
CLIENT_ID = "client"
AUTH_URL = f"{DOMAIN}/oauth2/authorize"
TOKEN_URL = f"{DOMAIN}/oauth2/token"
USERINFO_URL = f"{DOMAIN}/oauth2/userInfo"
JWKS_URL = f"{ISSUER}/.well-known/jwks.json"
DISCOVERY_URL = f"{ISSUER}/.well-known/openid-configuration"
DEFAULT_USERINFO_URL = f"{ISSUER}/oauth2/userInfo"

METADATA = {
    "issuer": ISSUER,
    "authorization_endpoint": AUTH_URL,
    "token_endpoint": TOKEN_URL,
    "userinfo_endpoint": USERINFO_URL,
    "jwks_uri": JWKS_URL,
}

# Throwaway RSA key for these tests only. The private half signs the ID
# tokens and JWT bearer assertions below; the public half is served through
# the fake JWKS endpoint and used to verify assertions. It is never used
# outside this file.
TEST_PRIVATE_KEY_PEM = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDRV/UMpGUSlPxC\nOFBFDk2oaCQKhxermGu0/u2KOu8WuzmvpXlVyXErFkbXuGMDiPHRyV5RWX5Bwmfr\nmobTbYaq5A6VVOh5hoWuICQU1qRWfH6ufTprXYUBH6WcIlmOjX6KPHwmc+AiRjfF\nqBGfsK5tQTgLQSS0oy7Jhu1d+/y5gSdQYiT0hlqXZqC4sfj7pW7t4hwa7XiCiCvT\ncnjcLIbzzYWWshQFt82u08CIZavRwRVUWRX6SUKvmOV0jCWzjvcAxVvTH8nDQk7p\nFjY+uz/nZeLgK+Dnu+xVjHB4rBfH6peKng/ML7ez+dH33oFLvC2531yzaWcW0Uk9\n7Q5GE6eHAgMBAAECggEAWNTTiZlKwE9TGcBuo1b18hO603LOwwRLFAMnBgSLBuDM\nkjGL4rC3olpyFkDKVyopvuUNbkSk9D+LvGiWdKohvmtGmuxsN4EzQZem5+bK1l4+\nnUlLXFrTQQ5ORoo26Ww2OW+AGQsLnU+hg/CVBefBpF/L6c6rRjGGfYKRP9PZQld8\nkdwZ2abTjeQ4a7NNYyKnwo4UZ5yVczjzRyTV2bMBoS0ITl5BFRuQLjtInp7YrRhD\nW8BVxbs2lw2c3ZIZCW5feJD5t/lIDo+AHOCxponMpctKLikvgXvEvxf2pj9IGX09\nIKgx4lcuDUhz3DJ/+g67wJQTzPy6XhAp1Luy0Z/UOQKBgQDxt3yMu+h8xkgAG/v/\nsSDS7iz6HPQK8KQCtOI8ElDtlXJ399Vuq/SyxmYCKroENFmvt9eGqk1s6/PgbL6N\nuUlX/kk7mar3RKVeJRYq5GJvk/d3zLoBo8y0FyTrPFU0dGKrHikcfYuyGg+SwohR\n97vyzwDDUIASDbs0fn1Wo9NUnwKBgQDdtsDW+1o+5C6CMqzleOUVdpyYjpe3PkF2\nfG0XSPfvZsESvDClfEIjX8905dV0QgtqhuYnDhmmDLv7xc4Al9aougY831R7q31A\n7GxZ62vYKwnIu6htSmmfebHqvh+khiKPks77+6hB5JXV+9AXb0w/B4l3ylSKZaNQ\nBwlR0XEcGQKBgQCCpSfecRnhhtIXrQhxVO1m1HDe5pNI7nPXOqkkysmPAD2UdhGX\n9b0We4FbHnjYGOt4vCbzlEyw2H9CB8SemUz5EGnImu/7IdE3p1fp6vMBV7pjt/W5\nOS1FEVVVB5EN/vHthym1Sm4c31UXf6lqlDmzrQq+hl4SY/WRE+Tu1TE+BQKBgArp\nCFpL6if4IJXFmp58MYG54YDcW3jn9l63RsMDkzfTraKXYilykOqet13ARZ2/9kHa\nu46mcfqq28FK/ZUn46dP6CissMKZMMO2HqraG+d6TrPzEBm4tLPlUC0GCBaXhzHb\nfpYFz0TW08zA5H+SuYTMgSZE7Z4V3FB+2CWPkepZAoGAT3BhBtnaeauv7zX/hTHS\nmxUI0ZNSkIRMihQnB5CiogxNtTK9bjZ05BfGINkRO8VvNitH6Qa18pEfK1mJV3Wv\njYzAro9YMCLRiGp8cVibK+WdLXEjfdEInLT7jbRNkaZuNi7abg+7+BMX1iInLZPI\ndwmn5AISPRKxmpl+rXQyeU8=\n-----END PRIVATE KEY-----\n"
TEST_JWK = {
    "kty": "RSA",
    "kid": "test-key-1",
    "use": "sig",
    "alg": "RS256",
    "n": "0Vf1DKRlEpT8QjhQRQ5NqGgkCocXq5hrtP7tijrvFrs5r6V5VclxKxZG17hjA4jx0cleUVl-QcJn65qG022GquQOlVToeYaFriAkFNakVnx-rn06a12FAR-lnCJZjo1-ijx8JnPgIkY3xagRn7CubUE4C0EktKMuyYbtXfv8uYEnUGIk9IZal2aguLH4-6Vu7eIcGu14gogr03J43CyG882FlrIUBbfNrtPAiGWr0cEVVFkV-klCr5jldIwls473AMVb0x_Jw0JO6RY2Prs_52Xi4Cvg57vsVYxweKwXx-qXip4PzC-3s_nR996BS7wtud9cs2lnFtFJPe0ORhOnhw",
    "e": "AQAB",
}
# Private half of TEST_JWK, for the OAuth 2.1 app-client JWT assertion.
TEST_PRIVATE_JWK = {
    "kty": "RSA",
    "kid": "test-key-1",
    "use": "sig",
    "alg": "RS256",
    "n": "0Vf1DKRlEpT8QjhQRQ5NqGgkCocXq5hrtP7tijrvFrs5r6V5VclxKxZG17hjA4jx0cleUVl-QcJn65qG022GquQOlVToeYaFriAkFNakVnx-rn06a12FAR-lnCJZjo1-ijx8JnPgIkY3xagRn7CubUE4C0EktKMuyYbtXfv8uYEnUGIk9IZal2aguLH4-6Vu7eIcGu14gogr03J43CyG882FlrIUBbfNrtPAiGWr0cEVVFkV-klCr5jldIwls473AMVb0x_Jw0JO6RY2Prs_52Xi4Cvg57vsVYxweKwXx-qXip4PzC-3s_nR996BS7wtud9cs2lnFtFJPe0ORhOnhw",
    "e": "AQAB",
    "d": "WNTTiZlKwE9TGcBuo1b18hO603LOwwRLFAMnBgSLBuDMkjGL4rC3olpyFkDKVyopvuUNbkSk9D-LvGiWdKohvmtGmuxsN4EzQZem5-bK1l4-nUlLXFrTQQ5ORoo26Ww2OW-AGQsLnU-hg_CVBefBpF_L6c6rRjGGfYKRP9PZQld8kdwZ2abTjeQ4a7NNYyKnwo4UZ5yVczjzRyTV2bMBoS0ITl5BFRuQLjtInp7YrRhDW8BVxbs2lw2c3ZIZCW5feJD5t_lIDo-AHOCxponMpctKLikvgXvEvxf2pj9IGX09IKgx4lcuDUhz3DJ_-g67wJQTzPy6XhAp1Luy0Z_UOQ",
    "p": "8bd8jLvofMZIABv7_7Eg0u4s-hz0CvCkArTiPBJQ7ZVyd_fVbqv0ssZmAiq6BDRZr7fXhqpNbOvz4Gy-jblJV_5JO5mq90SlXiUWKuRib5P3d8y6AaPMtBck6zxVNHRiqx4pHH2LshoPksKIUfe78s8Aw1CAEg27NH59VqPTVJ8",
    "q": "3bbA1vtaPuQugjKs5XjlFXacmI6Xtz5BdnxtF0j372bBErwwpXxCI1_PdOXVdEILaobmJw4Zpgy7-8XOAJfWqLoGPN9Ue6t9QOxsWetr2CsJyLuobUppn3mx6r4fpIYij5LO-_uoQeSV1fvQF29MPweJd8pUimWjUAcJUdFxHBk",
    "dp": "gqUn3nEZ4YbSF60IcVTtZtRw3uaTSO5z1zqpJMrJjwA9lHYRl_W9FnuBWx542BjreLwm85RMsNh_QgfEnplM-RBpyJrv-yHRN6dX6erzAVe6Y7f1uTktRRFVVQeRDf7x7YcptUpuHN9VF3-papQ5s60KvoZeEmP1kRPk7tUxPgU",
    "dq": "CukIWkvqJ_gglcWannwxgbnhgNxbeOf2XrdGwwOTN9OtopdiKXKQ6p63XcBFnb_2Qdq7jqZx-qrbwUr9lSfjp0_oKKywwpkww7Yeqtob53pOs_MQGbi0s-VQLQYIFpeHMdt-lgXPRNbTzMDkf5K5hMyBJkTtnhXcUH7YJY-R6lk",
    "qi": "T3BhBtnaeauv7zX_hTHSmxUI0ZNSkIRMihQnB5CiogxNtTK9bjZ05BfGINkRO8VvNitH6Qa18pEfK1mJV3WvjYzAro9YMCLRiGp8cVibK-WdLXEjfdEInLT7jbRNkaZuNi7abg-7-BMX1iInLZPIdwmn5AISPRKxmpl-rXQyeU8",
}


class FakeHTTPError(Exception):
    """Raised by the fake client when a canned response carries an error status."""


class DummyResponse:
    def __init__(self, payload: Dict[str, Any], status: int = 200):
        self._payload = payload
        self.status = status

    def raise_for_status(self) -> None:
        if self.status >= 400:
            raise FakeHTTPError(f"HTTP {self.status}")

    def json(self) -> Dict[str, Any]:
        return self._payload


class DummyClient:
    def __init__(self, factory: "DummyClientFactory"):
        self._factory = factory

    async def __aenter__(self) -> "DummyClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False

    async def post_retry(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        auth: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> DummyResponse:
        self._factory.calls.append(
            {
                "method": "POST",
                "url": url,
                "data": dict(data or {}),
                "auth": auth,
                "headers": dict(headers or {}),
            }
        )
        return self._factory.post_responses.pop(0)

    async def get_retry(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> DummyResponse:
        self._factory.calls.append(
            {"method": "GET", "url": url, "headers": dict(headers or {})}
        )
        return self._factory.get_responses.pop(0)


class DummyClientFactory:
    def __init__(
        self,
        *,
        post_responses: Optional[List[DummyResponse]] = None,
        get_responses: Optional[List[DummyResponse]] = None,
    ):
        self.post_responses = list(post_responses or [])
        self.get_responses = list(get_responses or [])
        self.calls: List[Dict[str, Any]] = []

    def __call__(self) -> DummyClient:
        return DummyClient(self)

    def posts(self) -> List[Dict[str, Any]]:
        return [c for c in self.calls if c["method"] == "POST"]

    def gets(self) -> List[Dict[str, Any]]:
        return [c for c in self.calls if c["method"] == "GET"]


def _make_id_token(
    *,
    sub: Optional[str] = "user-sub-1",
    email: Optional[str] = None,
    name: Optional[str] = None,
    given_name: Optional[str] = None,
) -> str:
    now = int(time.time())
    claims: Dict[str, Any] = {
        "iss": ISSUER,
        "aud": CLIENT_ID,
        "iat": now,
        "exp": now + 600,
    }
    if sub is not None:
        claims["sub"] = sub
    if email is not None:
        claims["email"] = email
    if name is not None:
        claims["name"] = name
    if given_name is not None:
        claims["given_name"] = given_name
    return jwt.encode(
        claims,
        TEST_PRIVATE_KEY_PEM,
        algorithm="RS256",
        headers={"kid": "test-key-1"},
    )


def _login(cls, factory, *, discovery_cache=True):
    instance = cls(
        issuer=ISSUER,
        client_id=CLIENT_ID,
        client_secret=SecretStr("secret"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"state-secret"),
    )
    # Direct assignment: see the injection note in the module docstring.
    instance._http_client_factory = factory
    if discovery_cache:
        instance._discovery = dict(METADATA)
    else:
        instance._discovery = None
    return instance


def _token_payload(*, id_token=None):
    payload: Dict[str, Any] = {
        "access_token": "access-123",
        "token_type": "Bearer",
        "expires_in": 3600,
    }
    if id_token is not None:
        payload["id_token"] = id_token
    return payload


def _assert_token_post(factory, *, code="auth-code-123") -> Dict[str, Any]:
    posts = factory.posts()
    assert len(posts) == 1
    post = posts[0]
    assert post["url"] == TOKEN_URL
    assert post["headers"] == {"Accept": "application/json"}
    assert post["auth"] is None
    data = post["data"]
    assert data["grant_type"] == "authorization_code"
    assert data["code"] == code
    assert data["redirect_uri"] == "https://example.com/callback"
    assert data["client_id"] == CLIENT_ID
    assert data["client_secret"] == "secret"
    assert data["code_verifier"]
    return data


def _assert_bearer_get(factory, url: str) -> Dict[str, Any]:
    gets = [c for c in factory.gets() if c["url"] == url]
    assert len(gets) == 1
    call = gets[0]
    assert call["headers"] == {
        "Accept": "application/json",
        "Authorization": "Bearer access-123",
    }
    return call


# --- CognitoOAuth20Login ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_auth_url_discovers_endpoints() -> None:
    factory = DummyClientFactory(
        get_responses=[DummyResponse(dict(METADATA))],
    )
    login = _login(CognitoOAuth20Login, factory, discovery_cache=False)
    payload = await login.auth_url()

    gets = factory.gets()
    assert len(gets) == 1
    assert gets[0]["url"] == DISCOVERY_URL
    assert gets[0]["headers"] == {"Accept": "application/json"}
    assert payload["url"].startswith(f"{AUTH_URL}?")
    params = parse_qs(urlsplit(payload["url"]).query)
    assert params["response_type"] == ["code"]
    assert params["client_id"] == [CLIENT_ID]
    assert params["redirect_uri"] == ["https://example.com/callback"]
    assert params["scope"] == ["openid email profile"]
    assert params["state"] == [payload["state"]]
    assert params["code_challenge_method"] == ["S256"]
    assert len(params["code_challenge"]) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_returns_identity_from_userinfo() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[
            DummyResponse(
                {
                    "sub": "user-sub-1",
                    "email": "user@example.com",
                    "name": "Example User",
                }
            )
        ],
    )
    login = _login(CognitoOAuth20Login, factory)
    payload = await login.auth_url()
    result = await login.exchange_and_identity("auth-code-123", payload["state"])

    _assert_token_post(factory)
    _assert_bearer_get(factory, USERINFO_URL)
    assert result["issuer"] == "cognito-oauth2"
    assert result["sub"] == "user-sub-1"
    assert result["email"] == "user@example.com"
    assert result["name"] == "Example User"
    assert result["raw"]["tokens"]["access_token"] == "access-123"
    assert result["raw"]["userinfo"]["email"] == "user@example.com"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_name_falls_back_to_given_name() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[
            DummyResponse(
                {
                    "sub": "user-sub-1",
                    "email": "user@example.com",
                    "given_name": "Example",
                }
            )
        ],
    )
    login = _login(CognitoOAuth20Login, factory)
    payload = await login.auth_url()
    result = await login.exchange_and_identity("auth-code-123", payload["state"])

    assert result["name"] == "Example"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_name_unknown_when_absent() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[
            DummyResponse({"sub": "user-sub-1", "email": "user@example.com"})
        ],
    )
    login = _login(CognitoOAuth20Login, factory)
    payload = await login.auth_url()
    result = await login.exchange_and_identity("auth-code-123", payload["state"])

    assert result["name"] == "Unknown"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_uses_default_userinfo_endpoint() -> None:
    metadata = {k: v for k, v in METADATA.items() if k != "userinfo_endpoint"}
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[
            DummyResponse(
                {
                    "sub": "user-sub-1",
                    "email": "user@example.com",
                    "name": "Example User",
                }
            )
        ],
    )
    login = _login(CognitoOAuth20Login, factory)
    login._discovery = metadata
    payload = await login.auth_url()
    result = await login.exchange_and_identity("auth-code-123", payload["state"])

    _assert_bearer_get(factory, DEFAULT_USERINFO_URL)
    assert result["sub"] == "user-sub-1"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_token_http_error_raises() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"error": "invalid_grant"}, status=400)],
    )
    login = _login(CognitoOAuth20Login, factory)
    payload = await login.auth_url()
    with pytest.raises(FakeHTTPError):
        await login.exchange_and_identity("auth-code-123", payload["state"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_missing_access_token_raises() -> None:
    factory = DummyClientFactory(post_responses=[DummyResponse({})])
    login = _login(CognitoOAuth20Login, factory)
    payload = await login.auth_url()
    # Current behavior: a token response without access_token raises KeyError.
    with pytest.raises(KeyError, match="access_token"):
        await login.exchange_and_identity("auth-code-123", payload["state"])


# --- CognitoOAuth21Login ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_exchange_returns_identity_from_id_token() -> None:
    id_token = _make_id_token(
        sub="user-sub-1",
        email="user@example.com",
        name="Example User",
    )
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload(id_token=id_token))],
        get_responses=[DummyResponse({"keys": [TEST_JWK]})],
    )
    login = _login(CognitoOAuth21Login, factory)
    payload = await login.auth_url()
    result = await login.exchange_and_identity("auth-code-123", payload["state"])

    _assert_token_post(factory)
    gets = factory.gets()
    assert [c["url"] for c in gets] == [JWKS_URL]
    assert gets[0]["headers"] == {"Accept": "application/json"}
    assert result["issuer"] == "cognito-oauth21"
    assert result["sub"] == "user-sub-1"
    assert result["email"] == "user@example.com"
    assert result["name"] == "Example User"
    assert result["raw"]["tokens"]["id_token"] == id_token


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_exchange_name_falls_back_to_given_name() -> None:
    id_token = _make_id_token(
        sub="user-sub-1",
        email="user@example.com",
        given_name="Example",
    )
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload(id_token=id_token))],
        get_responses=[DummyResponse({"keys": [TEST_JWK]})],
    )
    login = _login(CognitoOAuth21Login, factory)
    payload = await login.auth_url()
    result = await login.exchange_and_identity("auth-code-123", payload["state"])

    assert result["name"] == "Example"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_exchange_missing_id_token_raises() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[],
    )
    login = _login(CognitoOAuth21Login, factory)
    payload = await login.auth_url()
    with pytest.raises(ValueError, match="no id_token in response"):
        await login.exchange_and_identity("auth-code-123", payload["state"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_exchange_missing_sub_raises() -> None:
    id_token = _make_id_token(sub=None, email="user@example.com")
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload(id_token=id_token))],
        get_responses=[DummyResponse({"keys": [TEST_JWK]})],
    )
    login = _login(CognitoOAuth21Login, factory)
    payload = await login.auth_url()
    # Current behavior: an ID token without a sub claim raises KeyError.
    with pytest.raises(KeyError, match="sub"):
        await login.exchange_and_identity("auth-code-123", payload["state"])


# --- CognitoOIDC10Login ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_exchange_returns_claims() -> None:
    id_token = _make_id_token(
        sub="user-sub-1",
        email="user@example.com",
        name="Example User",
    )
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload(id_token=id_token))],
        get_responses=[DummyResponse({"keys": [TEST_JWK]})],
    )
    login = _login(CognitoOIDC10Login, factory)
    payload = await login.auth_url()
    result = await login.exchange("auth-code-123", payload["state"])

    _assert_token_post(factory)
    gets = factory.gets()
    # Claims are complete, so no UserInfo call is made.
    assert [c["url"] for c in gets] == [JWKS_URL]
    assert result["issuer"] == "cognito-oidc"
    assert result["sub"] == "user-sub-1"
    assert result["email"] == "user@example.com"
    assert result["name"] == "Example User"
    assert result["raw"]["tokens"]["id_token"] == id_token


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_exchange_userinfo_fills_missing_email() -> None:
    id_token = _make_id_token(sub="user-sub-1", name="Example User")
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload(id_token=id_token))],
        get_responses=[
            DummyResponse({"keys": [TEST_JWK]}),
            DummyResponse({"email": "filled@example.com"}),
        ],
    )
    login = _login(CognitoOIDC10Login, factory)
    payload = await login.auth_url()
    result = await login.exchange("auth-code-123", payload["state"])

    _assert_bearer_get(factory, USERINFO_URL)
    assert result["sub"] == "user-sub-1"
    assert result["email"] == "filled@example.com"
    # Name already present in the claims is kept.
    assert result["name"] == "Example User"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_exchange_userinfo_fills_unknown_name() -> None:
    id_token = _make_id_token(sub="user-sub-1", email="user@example.com")
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload(id_token=id_token))],
        get_responses=[
            DummyResponse({"keys": [TEST_JWK]}),
            DummyResponse({"name": "Userinfo User"}),
        ],
    )
    login = _login(CognitoOIDC10Login, factory)
    payload = await login.auth_url()
    result = await login.exchange("auth-code-123", payload["state"])

    _assert_bearer_get(factory, USERINFO_URL)
    assert result["email"] == "user@example.com"
    assert result["name"] == "Userinfo User"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_exchange_missing_id_token_raises() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[],
    )
    login = _login(CognitoOIDC10Login, factory)
    payload = await login.auth_url()
    with pytest.raises(ValueError, match="no id_token in response"):
        await login.exchange("auth-code-123", payload["state"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_exchange_token_http_error_raises() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"error": "invalid_grant"}, status=400)],
    )
    login = _login(CognitoOIDC10Login, factory)
    payload = await login.auth_url()
    with pytest.raises(FakeHTTPError):
        await login.exchange("auth-code-123", payload["state"])


# --- CognitoOAuth20AppClient ---


def _app_client20(factory, *, scope=None):
    client = CognitoOAuth20AppClient(
        base_url=DOMAIN,
        client_id=CLIENT_ID,
        client_secret=SecretStr("secret"),
    )
    # Direct assignment: see the injection note in the module docstring.
    client._http_client_factory = factory
    return client


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_app_client_posts_client_credentials() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"access_token": "app-token"})],
    )
    client = _app_client20(factory)
    token = await client.access_token()

    assert token == "app-token"
    posts = factory.posts()
    assert len(posts) == 1
    post = posts[0]
    assert post["url"] == TOKEN_URL
    assert post["headers"] == {"Accept": "application/json"}
    assert post["auth"] == (CLIENT_ID, "secret")
    assert post["data"] == {"grant_type": "client_credentials"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_app_client_sends_scope() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"access_token": "app-token"})],
    )
    client = _app_client20(factory)
    token = await client.access_token("scope-a")

    assert token == "app-token"
    posts = factory.posts()
    assert len(posts) == 1
    assert posts[0]["data"] == {
        "grant_type": "client_credentials",
        "scope": "scope-a",
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_app_client_caches_token() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"access_token": "app-token"})],
    )
    client = _app_client20(factory)
    first = await client.access_token()
    second = await client.access_token()

    assert first == second == "app-token"
    assert len(factory.posts()) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_app_client_missing_access_token_raises() -> None:
    factory = DummyClientFactory(post_responses=[DummyResponse({})])
    client = _app_client20(factory)
    # Current behavior: a token response without access_token raises KeyError.
    with pytest.raises(KeyError, match="access_token"):
        await client.access_token()


# --- CognitoOAuth21AppClient ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_app_client_secret_posts_basic_auth() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"access_token": "app-token"})],
    )
    client = CognitoOAuth21AppClient(
        base_url=DOMAIN,
        client_id=CLIENT_ID,
        client_secret=SecretStr("secret"),
    )
    client._http_client_factory = factory
    token = await client.access_token()

    assert token == "app-token"
    posts = factory.posts()
    assert len(posts) == 1
    post = posts[0]
    assert post["url"] == TOKEN_URL
    assert post["headers"] == {"Accept": "application/json"}
    assert post["auth"] == (CLIENT_ID, "secret")
    assert post["data"] == {"grant_type": "client_credentials"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_app_client_jwk_posts_jwt_assertion() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"access_token": "app-token"})],
    )
    client = CognitoOAuth21AppClient(
        base_url=DOMAIN,
        client_id=CLIENT_ID,
        private_key_jwk=dict(TEST_PRIVATE_JWK),
    )
    client._http_client_factory = factory
    token = await client.access_token()

    assert token == "app-token"
    posts = factory.posts()
    assert len(posts) == 1
    post = posts[0]
    assert post["url"] == TOKEN_URL
    assert post["headers"] == {"Accept": "application/json"}
    assert post["auth"] is None
    data = post["data"]
    assert data["grant_type"] == "client_credentials"
    assert data["client_id"] == CLIENT_ID
    assert (
        data["client_assertion_type"]
        == "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
    )
    assertion = jwt.decode(
        data["client_assertion"],
        jwt.algorithms.RSAAlgorithm.from_jwk(TEST_JWK),
        algorithms=["RS256"],
        audience=TOKEN_URL,
    )
    assert assertion["iss"] == CLIENT_ID
    assert assertion["sub"] == CLIENT_ID
    assert assertion["aud"] == TOKEN_URL
    assert assertion["exp"] - assertion["iat"] == 300
    header = jwt.get_unverified_header(data["client_assertion"])
    assert header["kid"] == "test-key-1"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_app_client_missing_access_token_raises() -> None:
    factory = DummyClientFactory(post_responses=[DummyResponse({})])
    client = CognitoOAuth21AppClient(
        base_url=DOMAIN,
        client_id=CLIENT_ID,
        client_secret=SecretStr("secret"),
    )
    client._http_client_factory = factory
    # Current behavior: a token response without access_token raises KeyError.
    with pytest.raises(KeyError, match="access_token"):
        await client.access_token()


# --- CognitoOIDC10AppClient ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_app_client_discovers_then_posts_token() -> None:
    factory = DummyClientFactory(
        post_responses=[
            DummyResponse({"access_token": "oidc-app-token"}),
            DummyResponse({"access_token": "oidc-app-token-2"}),
        ],
        get_responses=[DummyResponse(dict(METADATA))],
    )
    client = CognitoOIDC10AppClient(
        issuer=ISSUER,
        client_id=CLIENT_ID,
        client_secret=SecretStr("secret"),
    )
    client._http_client_factory = factory

    token_one = await client.access_token()
    # Force a refresh so the second call posts again.
    client._cached_token = ("oidc-app-token", time.time() - 100)
    token_two = await client.access_token()

    assert token_one == "oidc-app-token"
    assert token_two == "oidc-app-token-2"
    # Discovery happens once; each token call still posts.
    gets = factory.gets()
    assert len(gets) == 1
    assert gets[0]["url"] == DISCOVERY_URL
    assert gets[0]["headers"] == {"Accept": "application/json"}
    posts = factory.posts()
    assert len(posts) == 2
    assert all(p["url"] == TOKEN_URL for p in posts)
    assert all(p["auth"] == (CLIENT_ID, "secret") for p in posts)
    assert all(p["data"] == {"grant_type": "client_credentials"} for p in posts)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_app_client_caches_token() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"access_token": "oidc-app-token"})],
        get_responses=[DummyResponse(dict(METADATA))],
    )
    client = CognitoOIDC10AppClient(
        issuer=ISSUER,
        client_id=CLIENT_ID,
        client_secret=SecretStr("secret"),
    )
    client._http_client_factory = factory
    first = await client.access_token()
    second = await client.access_token()

    assert first == second == "oidc-app-token"
    assert len(factory.gets()) == 1
    assert len(factory.posts()) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_app_client_missing_token_endpoint_raises() -> None:
    factory = DummyClientFactory(
        post_responses=[],
        get_responses=[DummyResponse({"issuer": ISSUER})],
    )
    client = CognitoOIDC10AppClient(
        issuer=ISSUER,
        client_id=CLIENT_ID,
        client_secret=SecretStr("secret"),
    )
    client._http_client_factory = factory
    # Current behavior: discovery without a token_endpoint raises KeyError.
    with pytest.raises(KeyError, match="token_endpoint"):
        await client.access_token()
