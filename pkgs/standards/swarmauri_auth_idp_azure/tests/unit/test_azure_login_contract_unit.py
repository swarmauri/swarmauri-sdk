"""Offline contract tests for the Azure login flows (#6276).

Covers the primary public operation of each exported class, which the
existing unit tests only touch through construction, ``auth_url`` PKCE
checks, and monkeypatched exchanges:

- ``AzureOAuth20Login.exchange_and_identity``: token exchange + Graph
  profile mapping (including the ``mail``/``userPrincipalName`` email
  fallback), the missing-``access_token`` behavior (no profile fetch),
  and token/profile HTTP errors.
- ``AzureOAuth21Login.exchange_and_identity``: the same contract, plus
  the ``prompt=select_account`` request in ``auth_url``.
- ``AzureOIDC10Login.exchange``: discovery through the fake client,
  token exchange + ID token verification against a fake JWKS endpoint,
  the ``preferred_username``/``given_name`` claim fallbacks, the
  missing-``id_token`` behavior, and the missing/unknown-``kid``
  failures.

Everything runs offline: a fake HTTP client serves discovery metadata,
token responses, Graph profiles, and JWKS, and the ID tokens are signed
with a throwaway RSA key generated for these tests. No network access,
credentials, or live Azure tenant are needed, and nothing here proves
interoperability with Microsoft Entra ID's production service.

Injection note: the fake client is installed by direct instance
assignment (``login._http_client_factory = factory``), the same approach
the existing Cognito tests use for ``_discovery``. The constructor
rejects the factory as an extra input (``extra="forbid"`` on the OIDC
login and on the mixin-based logins). For the OAuth 2.0/2.1 logins the
factory lives on ``AzureLoginMixin`` as a private attribute, which
pydantic does not install on the model (see the PR body: a fresh
OAuth 2.0/2.1 login instance cannot run ``exchange_and_identity`` at
all without this assignment).
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlsplit

import jwt
import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_azure import (
    AzureOAuth20Login,
    AzureOAuth21Login,
    AzureOIDC10Login,
)

TENANT = "contoso.onmicrosoft.com"
CLIENT_ID = "client-id"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT}/oauth2/v2.0"
AUTH_URL = f"{AUTHORITY}/authorize"
TOKEN_URL = f"{AUTHORITY}/token"
GRAPH_URL = "https://graph.microsoft.com/v1.0/me"
DISCOVERY_URL = (
    f"https://login.microsoftonline.com/{TENANT}/v2.0/.well-known/openid-configuration"
)
OIDC_ISSUER = "https://login.microsoftonline.com/tenant-id-guid/v2.0"
OIDC_AUTH_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
OIDC_TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
OIDC_JWKS_URL = "https://login.microsoftonline.com/common/discovery/v2.0/keys"

METADATA = {
    "issuer": OIDC_ISSUER,
    "authorization_endpoint": OIDC_AUTH_URL,
    "token_endpoint": OIDC_TOKEN_URL,
    "jwks_uri": OIDC_JWKS_URL,
}

# Throwaway RSA key for these tests only. The private half signs the ID
# tokens below; the public half is served through the fake JWKS endpoint.
# It is never used outside this file.
TEST_PRIVATE_KEY_PEM = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDRV/UMpGUSlPxC\nOFBFDk2oaCQKhxermGu0/u2KOu8WuzmvpXlVyXErFkbXuGMDiPHRyV5RWX5Bwmfr\nmobTbYaq5A6VVOh5hoWuICQU1qRWfH6ufTprXYUBH6WcIlmOjX6KPHwmc+AiRjfF\nqBGfsK5tQTgLQSS0oy7Jhu1d+/y5gSdQYiT0hlqXZqC4sfj7pW7t4hwa7XiCiCvT\ncnjcLIbzzYWWshQFt82u08CIZavRwRVUWRX6SUKvmOV0jCWzjvcAxVvTH8nDQk7p\nFjY+uz/nZeLgK+Dnu+xVjHB4rBfH6peKng/ML7ez+dH33oFLvC2531yzaWcW0Uk9\n7Q5GE6eHAgMBAAECggEAWNTTiZlKwE9TGcBuo1b18hO603LOwwRLFAMnBgSLBuDM\nkjGL4rC3olpyFkDKVyopvuUNbkSk9D+LvGiWdKohvmtGmuxsN4EzQZem5+bK1l4+\nnUlLXFrTQQ5ORoo26Ww2OW+AGQsLnU+hg/CVBefBpF/L6c6rRjGGfYKRP9PZQld8\nkdwZ2abTjeQ4a7NNYyKnwo4UZ5yVczjzRyTV2bMBoS0ITl5BFRuQLjtInp7YrRhD\nW8BVxbs2lw2c3ZIZCW5feJD5t/lIDo+AHOCxponMpctKLikvgXvEvxf2pj9IGX09\nIKgx4lcuDUhz3DJ/+g67wJQTzPy6XhAp1Luy0Z/UOQKBgQDxt3yMu+h8xkgAG/v/\nsSDS7iz6HPQK8KQCtOI8ElDtlXJ399Vuq/SyxmYCKroENFmvt9eGqk1s6/PgbL6N\nuUlX/kk7mar3RKVeJRYq5GJvk/d3zLoBo8y0FyTrPFU0dGKrHikcfYuyGg+SwohR\n97vyzwDDUIASDbs0fn1Wo9NUnwKBgQDdtsDW+1o+5C6CMqzleOUVdpyYjpe3PkF2\nfG0XSPfvZsESvDClfEIjX8905dV0QgtqhuYnDhmmDLv7xc4Al9aougY831R7q31A\n7GxZ62vYKwnIu6htSmmfebHqvh+khiKPks77+6hB5JXV+9AXb0w/B4l3ylSKZaNQ\nBwlR0XEcGQKBgQCCpSfecRnhhtIXrQhxVO1m1HDe5pNI7nPXOqkkysmPAD2UdhGX\n9b0We4FbHnjYGOt4vCbzlEyw2H9CB8SemUz5EGnImu/7IdE3p1fp6vMBV7pjt/W5\nOS1FEVVVB5EN/vHthym1Sm4c31UXf6lqlDmzrQq+hl4SY/WRE+Tu1TE+BQKBgArp\nCFpL6if4IJXFmp58MYG54YDcW3jn9l63RsMDkzfTraKXYilykOqet13ARZ2/9kHa\nu46mcfqq28FK/ZUn46dP6CissMKZMMO2HqraG+d6TrPzEBm4tLPlUC0GCBaXhzHb\nfpYFz0TW08zA5H+SuYTMgSZE7Z4V3FB+2CWPkepZAoGAT3BhBtnaeauv7zX/hTHS\nmxUI0ZNSkIRMihQnB5CiogxNtTK9bjZ05BfGINkRO8VvNitH6Qa18pEfK1mJV3Wv\njYzAro9YMCLRiGp8cVibK+WdLXEjfdEInLT7jbRNkaZuNi7abg+7+BMX1iInLZPI\ndwmn5AISPRKxmpl+rXQyeU8=\n-----END PRIVATE KEY-----\n"
TEST_JWK = {
    "kty": "RSA",
    "kid": "test-key-1",
    "use": "sig",
    "alg": "RS256",
    "n": "0Vf1DKRlEpT8QjhQRQ5NqGgkCocXq5hrtP7tijrvFrs5r6V5VclxKxZG17hjA4jx0cleUVl-QcJn65qG022GquQOlVToeYaFriAkFNakVnx-rn06a12FAR-lnCJZjo1-ijx8JnPgIkY3xagRn7CubUE4C0EktKMuyYbtXfv8uYEnUGIk9IZal2aguLH4-6Vu7eIcGu14gogr03J43CyG882FlrIUBbfNrtPAiGWr0cEVVFkV-klCr5jldIwls473AMVb0x_Jw0JO6RY2Prs_52Xi4Cvg57vsVYxweKwXx-qXip4PzC-3s_nR996BS7wtud9cs2lnFtFJPe0ORhOnhw",
    "e": "AQAB",
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
    sub: Optional[str] = "user-id",
    email: Optional[str] = None,
    name: Optional[str] = None,
    given_name: Optional[str] = None,
    preferred_username: Optional[str] = None,
    kid: Optional[str] = "test-key-1",
) -> str:
    now = int(time.time())
    claims: Dict[str, Any] = {
        "iss": OIDC_ISSUER,
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
    if preferred_username is not None:
        claims["preferred_username"] = preferred_username
    headers = {"kid": kid} if kid is not None else None
    return jwt.encode(
        claims,
        TEST_PRIVATE_KEY_PEM,
        algorithm="RS256",
        headers=headers,
    )


def _login(cls, factory, *, discovery_cache=True):
    instance = cls(
        tenant=TENANT,
        client_id=CLIENT_ID,
        client_secret=SecretStr("client-secret"),
        redirect_uri="https://app.example.com/callback",
        state_secret=b"state-secret",
    )
    # Direct assignment: see the injection note in the module docstring.
    instance._http_client_factory = factory
    if hasattr(instance, "_discovery"):
        instance._discovery = dict(METADATA) if discovery_cache else None
    return instance


def _token_payload(*, access_token="access-token", id_token=None):
    payload: Dict[str, Any] = {"access_token": access_token}
    if id_token is not None:
        payload["id_token"] = id_token
    return payload


def _graph_profile(*, mail="user@example.com", upn=None):
    profile: Dict[str, Any] = {
        "id": "user-id",
        "displayName": "Example User",
    }
    if mail is not None:
        profile["mail"] = mail
    if upn is not None:
        profile["userPrincipalName"] = upn
    return profile


def _assert_mixin_token_post(factory, *, code="auth-code") -> Dict[str, Any]:
    posts = factory.posts()
    assert len(posts) == 1
    post = posts[0]
    assert post["url"] == TOKEN_URL
    assert post["headers"] == {"Accept": "application/json"}
    assert post["auth"] is None
    data = post["data"]
    assert data["grant_type"] == "authorization_code"
    assert data["code"] == code
    assert data["redirect_uri"] == "https://app.example.com/callback"
    assert data["client_id"] == CLIENT_ID
    assert data["client_secret"] == "client-secret"
    assert data["code_verifier"]
    assert data["scope"] == "User.Read offline_access"
    return data


def _assert_graph_get(factory) -> Dict[str, Any]:
    gets = [c for c in factory.gets() if c["url"] == GRAPH_URL]
    assert len(gets) == 1
    call = gets[0]
    assert call["headers"] == {
        "Authorization": "Bearer access-token",
        "Accept": "application/json",
    }
    return call


def _assert_auth_url_params(payload, *, prompt=None):
    assert payload["url"].startswith(f"{AUTH_URL}?")
    params = parse_qs(urlsplit(payload["url"]).query)
    assert params["response_type"] == ["code"]
    assert params["client_id"] == [CLIENT_ID]
    assert params["redirect_uri"] == ["https://app.example.com/callback"]
    assert params["scope"] == ["User.Read offline_access"]
    assert params["state"] == [payload["state"]]
    assert params["code_challenge_method"] == ["S256"]
    assert len(params["code_challenge"]) == 1
    if prompt is None:
        assert "prompt" not in params
    else:
        assert params["prompt"] == [prompt]


# --- AzureOAuth20Login ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_auth_url_uses_tenant_endpoints() -> None:
    factory = DummyClientFactory()
    login = _login(AzureOAuth20Login, factory)
    payload = await login.auth_url()

    _assert_auth_url_params(payload)
    # auth_url is computed locally; no HTTP call is made.
    assert factory.calls == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_returns_graph_profile() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[DummyResponse(_graph_profile())],
    )
    login = _login(AzureOAuth20Login, factory)
    payload = await login.auth_url()
    result = await login.exchange_and_identity("auth-code", payload["state"])

    _assert_mixin_token_post(factory)
    _assert_graph_get(factory)
    assert result["issuer"] == "azure-oauth20"
    assert result["tokens"] == {"access_token": "access-token"}
    assert result["profile"]["id"] == "user-id"
    assert result["sub"] == "user-id"
    assert result["email"] == "user@example.com"
    assert result["name"] == "Example User"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_email_falls_back_to_upn() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[
            DummyResponse(_graph_profile(mail=None, upn="user@contoso.onmicrosoft.com"))
        ],
    )
    login = _login(AzureOAuth20Login, factory)
    payload = await login.auth_url()
    result = await login.exchange_and_identity("auth-code", payload["state"])

    assert result["email"] == "user@contoso.onmicrosoft.com"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_missing_access_token_skips_profile() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({})],
        get_responses=[],
    )
    login = _login(AzureOAuth20Login, factory)
    payload = await login.auth_url()
    result = await login.exchange_and_identity("auth-code", payload["state"])

    assert factory.gets() == []
    assert result["profile"] == {}
    assert result["sub"] is None
    assert result["email"] is None
    assert result["name"] is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_token_http_error_raises() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"error": "invalid_grant"}, status=400)],
    )
    login = _login(AzureOAuth20Login, factory)
    payload = await login.auth_url()
    with pytest.raises(FakeHTTPError):
        await login.exchange_and_identity("auth-code", payload["state"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_profile_http_error_raises() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[DummyResponse({"error": "boom"}, status=500)],
    )
    login = _login(AzureOAuth20Login, factory)
    payload = await login.auth_url()
    with pytest.raises(FakeHTTPError):
        await login.exchange_and_identity("auth-code", payload["state"])


# --- AzureOAuth21Login ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_auth_url_requests_select_account() -> None:
    login = _login(AzureOAuth21Login, DummyClientFactory())
    payload = await login.auth_url()

    _assert_auth_url_params(payload, prompt="select_account")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_exchange_returns_graph_profile() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[DummyResponse(_graph_profile())],
    )
    login = _login(AzureOAuth21Login, factory)
    payload = await login.auth_url()
    result = await login.exchange_and_identity("auth-code", payload["state"])

    _assert_mixin_token_post(factory)
    _assert_graph_get(factory)
    assert result["issuer"] == "azure-oauth21"
    assert result["sub"] == "user-id"
    assert result["email"] == "user@example.com"
    assert result["name"] == "Example User"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_exchange_email_falls_back_to_upn() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[
            DummyResponse(_graph_profile(mail=None, upn="user@contoso.onmicrosoft.com"))
        ],
    )
    login = _login(AzureOAuth21Login, factory)
    payload = await login.auth_url()
    result = await login.exchange_and_identity("auth-code", payload["state"])

    assert result["email"] == "user@contoso.onmicrosoft.com"


# --- AzureOIDC10Login ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_auth_url_discovers_endpoints() -> None:
    factory = DummyClientFactory(
        get_responses=[DummyResponse(dict(METADATA))],
    )
    login = _login(AzureOIDC10Login, factory, discovery_cache=False)
    payload = await login.auth_url()

    gets = factory.gets()
    assert len(gets) == 1
    assert gets[0]["url"] == DISCOVERY_URL
    assert gets[0]["headers"] == {"Accept": "application/json"}
    assert payload["url"].startswith(f"{OIDC_AUTH_URL}?")
    params = parse_qs(urlsplit(payload["url"]).query)
    assert params["response_type"] == ["code"]
    assert params["client_id"] == [CLIENT_ID]
    assert params["redirect_uri"] == ["https://app.example.com/callback"]
    assert params["scope"] == ["openid profile email"]
    assert params["state"] == [payload["state"]]
    assert params["code_challenge_method"] == ["S256"]
    assert len(params["code_challenge"]) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_exchange_returns_claims() -> None:
    id_token = _make_id_token(
        sub="user-id",
        email="user@example.com",
        name="Example User",
    )
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload(id_token=id_token))],
        get_responses=[DummyResponse({"keys": [TEST_JWK]})],
    )
    login = _login(AzureOIDC10Login, factory)
    payload = await login.auth_url()
    result = await login.exchange("auth-code", payload["state"])

    posts = factory.posts()
    assert len(posts) == 1
    post = posts[0]
    assert post["url"] == OIDC_TOKEN_URL
    assert post["headers"] == {"Accept": "application/json"}
    assert post["auth"] is None
    data = post["data"]
    assert data["grant_type"] == "authorization_code"
    assert data["code"] == "auth-code"
    assert data["redirect_uri"] == "https://app.example.com/callback"
    assert data["client_id"] == CLIENT_ID
    assert data["client_secret"] == "client-secret"
    assert data["code_verifier"]
    # The OIDC exchange form carries no scope (unlike the mixin logins).
    assert "scope" not in data
    gets = factory.gets()
    assert [c["url"] for c in gets] == [OIDC_JWKS_URL]
    assert result["issuer"] == "azure-oidc10"
    assert result["claims"]["sub"] == "user-id"
    assert result["sub"] == "user-id"
    assert result["email"] == "user@example.com"
    assert result["name"] == "Example User"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_exchange_email_falls_back_to_preferred_username() -> None:
    id_token = _make_id_token(
        sub="user-id",
        preferred_username="user@contoso.onmicrosoft.com",
        name="Example User",
    )
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload(id_token=id_token))],
        get_responses=[DummyResponse({"keys": [TEST_JWK]})],
    )
    login = _login(AzureOIDC10Login, factory)
    payload = await login.auth_url()
    result = await login.exchange("auth-code", payload["state"])

    assert result["email"] == "user@contoso.onmicrosoft.com"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_exchange_name_falls_back_to_given_name() -> None:
    id_token = _make_id_token(
        sub="user-id",
        email="user@example.com",
        given_name="Example",
    )
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload(id_token=id_token))],
        get_responses=[DummyResponse({"keys": [TEST_JWK]})],
    )
    login = _login(AzureOIDC10Login, factory)
    payload = await login.auth_url()
    result = await login.exchange("auth-code", payload["state"])

    assert result["name"] == "Example"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_exchange_missing_id_token_returns_empty_claims() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[],
    )
    login = _login(AzureOIDC10Login, factory)
    payload = await login.auth_url()
    result = await login.exchange("auth-code", payload["state"])

    # Current behavior: a missing id_token yields empty claims instead of
    # raising; no JWKS call is made.
    assert factory.gets() == []
    assert result["claims"] == {}
    assert result["sub"] is None
    assert result["email"] is None
    assert result["name"] is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_exchange_token_http_error_raises() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"error": "invalid_grant"}, status=400)],
    )
    login = _login(AzureOIDC10Login, factory)
    payload = await login.auth_url()
    with pytest.raises(FakeHTTPError):
        await login.exchange("auth-code", payload["state"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_exchange_missing_kid_raises() -> None:
    id_token = _make_id_token(sub="user-id", kid=None)
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload(id_token=id_token))],
        get_responses=[DummyResponse({"keys": [TEST_JWK]})],
    )
    login = _login(AzureOIDC10Login, factory)
    payload = await login.auth_url()
    with pytest.raises(ValueError, match="kid missing from id_token header"):
        await login.exchange("auth-code", payload["state"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_exchange_unknown_kid_raises() -> None:
    id_token = _make_id_token(sub="user-id", kid="unknown-kid")
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload(id_token=id_token))],
        get_responses=[DummyResponse({"keys": [TEST_JWK]})],
    )
    login = _login(AzureOIDC10Login, factory)
    payload = await login.auth_url()
    with pytest.raises(ValueError, match="signing key not found for id_token"):
        await login.exchange("auth-code", payload["state"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_discovery_reused_across_calls() -> None:
    id_token = _make_id_token(
        sub="user-id",
        email="user@example.com",
        name="Example User",
    )
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload(id_token=id_token))],
        get_responses=[
            DummyResponse(dict(METADATA)),
            DummyResponse({"keys": [TEST_JWK]}),
        ],
    )
    login = _login(AzureOIDC10Login, factory, discovery_cache=False)
    payload = await login.auth_url()
    result = await login.exchange("auth-code", payload["state"])

    assert result["sub"] == "user-id"
    gets = factory.gets()
    # Discovery is fetched once by auth_url; exchange reuses it and only
    # fetches the JWKS.
    assert [c["url"] for c in gets] == [DISCOVERY_URL, OIDC_JWKS_URL]
