"""Offline contract tests for the Salesforce login flows (#6297).

Covers the primary public operation of each exported class, which the
existing unit tests only touch through construction, ``auth_url`` prefix
checks, and invalid-state failures:

- ``SalesforceOAuth20Login.exchange_and_identity``: token exchange +
  UserInfo mapping, and the identity-endpoint fallback when UserInfo is
  empty or errors.
- ``SalesforceOAuth21Login.exchange_and_identity``: discovery through the
  fake client, token exchange + ID token verification against a fake JWKS
  endpoint, and the UserInfo fallback when the claims are incomplete.
- ``SalesforceOIDC10Login.exchange``: token exchange + ID token
  verification, with the UserInfo fallback only when the claims are
  incomplete, and the missing-``id_token`` failure.
- ``SalesforceOAuth20AppClient.access_token``: real JWT bearer assertion
  contents (issuer, subject, audience, lifetime), scope passthrough, and
  the missing-``access_token`` failure.
- ``SalesforceOAuth21AppClient.access_token``: delegation to the OAuth 2.0
  JWT bearer client is covered by the existing unit test; the real JWK
  signing path is NOT covered here because ``_jwt_assertion`` passes the
  JWK dict straight to ``jwt.encode``, which current PyJWT rejects with
  ``TypeError: Expecting a PEM-formatted key`` (see the PR body — tracked
  separately as a runtime defect, not fixed in this tests-only change).
- ``SalesforceOIDC10AppClient.access_token``: discovery through the fake
  client, token endpoint resolution (including the default fallback), and
  discovery reuse across calls.

Everything runs offline: a fake HTTP client serves discovery metadata,
token responses, UserInfo, identity, and JWKS, and the ID tokens and JWT
assertions are signed with a throwaway RSA key generated for these tests.
No network access, credentials, or live Salesforce account are needed,
and nothing here proves interoperability with Salesforce's production
service.
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlsplit

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_salesforce import (
    SalesforceOAuth20AppClient,
    SalesforceOAuth20Login,
    SalesforceOAuth21Login,
    SalesforceOIDC10AppClient,
    SalesforceOIDC10Login,
)

BASE_URL = "https://login.salesforce.com"
CLIENT_ID = "client"
USER = "user@example.com"
TOKEN_URL = f"{BASE_URL}/services/oauth2/token"
AUTH_URL = f"{BASE_URL}/services/oauth2/authorize"
USERINFO_URL = f"{BASE_URL}/services/oauth2/userinfo"
JWKS_URL = f"{BASE_URL}/services/oauth2/certs"
DISCOVERY_URL = f"{BASE_URL}/.well-known/openid-configuration"
IDENTITY_URL = f"{BASE_URL}/id/00Dxx0000000001/005xx0000000001"

METADATA = {
    "issuer": BASE_URL,
    "authorization_endpoint": AUTH_URL,
    "token_endpoint": TOKEN_URL,
    "userinfo_endpoint": USERINFO_URL,
    "jwks_uri": JWKS_URL,
}

# Throwaway RSA key for these tests only. The private half signs the ID
# tokens and JWT bearer assertions below; the public half is served through
# the fake JWKS endpoint and used to verify assertions. It is never used
# outside this file.
_RSA_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
TEST_PRIVATE_KEY_PEM = _RSA_KEY.private_bytes(
    serialization.Encoding.PEM,
    serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption(),
).decode("ascii")
TEST_JWK = json.loads(
    jwt.algorithms.RSAAlgorithm.to_jwk(_RSA_KEY.public_key())
)
TEST_JWK.update(kid="test-key-1", use="sig", alg="RS256")
TEST_JWKS = {"keys": [TEST_JWK]}


class FakeHTTPError(Exception):
    """Raised by the fake client when a canned response carries an
    error status."""


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
    sub: str,
    email: Optional[str] = None,
    name: Optional[str] = None,
    preferred_username: Optional[str] = None,
) -> str:
    now = int(time.time())
    claims: Dict[str, Any] = {
        "sub": sub,
        "iss": BASE_URL,
        "aud": CLIENT_ID,
        "iat": now,
        "exp": now + 600,
    }
    if email is not None:
        claims["email"] = email
    if name is not None:
        claims["name"] = name
    if preferred_username is not None:
        claims["preferred_username"] = preferred_username
    return jwt.encode(
        claims,
        TEST_PRIVATE_KEY_PEM,
        algorithm="RS256",
        headers={"kid": "test-key-1"},
    )


def _login(cls, factory, *, discovery_cache=True):
    instance = cls(
        base_url=BASE_URL,
        client_id=CLIENT_ID,
        client_secret=SecretStr("secret"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"state-secret"),
        http_client_factory=factory,
    )
    if discovery_cache and hasattr(instance, "discovery_cache"):
        instance.discovery_cache = dict(METADATA)
    return instance


def _token_payload(*, id_token=None, identity_url=None):
    payload: Dict[str, Any] = {
        "access_token": "access-123",
        "token_type": "Bearer",
        "expires_in": 3600,
        "id": identity_url or IDENTITY_URL,
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
        "Authorization": "Bearer access-123",
        "Accept": "application/json",
    }
    return call


# --- SalesforceOAuth20Login ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_auth_url_uses_configured_base() -> None:
    factory = DummyClientFactory()
    login = _login(SalesforceOAuth20Login, factory)
    payload = await login.auth_url()

    assert payload["url"].startswith(f"{AUTH_URL}?")
    params = parse_qs(urlsplit(payload["url"]).query)
    assert params["response_type"] == ["code"]
    assert params["client_id"] == [CLIENT_ID]
    assert params["redirect_uri"] == ["https://example.com/callback"]
    assert params["scope"] == ["refresh_token"]
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
                    "sub": "005xx0000000001",
                    "user_id": "005xx0000000001",
                    "email": "user@example.com",
                    "name": "Example User",
                }
            )
        ],
    )
    login = _login(SalesforceOAuth20Login, factory)
    payload = await login.auth_url()
    result = await login.exchange_and_identity(
        "auth-code-123", payload["state"]
    )

    _assert_token_post(factory)
    _assert_bearer_get(factory, USERINFO_URL)
    assert result["issuer"] == "salesforce-oauth20"
    assert result["sub"] == "005xx0000000001"
    assert result["email"] == "user@example.com"
    assert result["name"] == "Example User"
    assert result["raw"]["tokens"]["access_token"] == "access-123"
    assert result["raw"]["userinfo"]["email"] == "user@example.com"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_falls_back_to_identity_endpoint() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[
            DummyResponse({}),
            DummyResponse(
                {
                    "user_id": "005xx0000000002",
                    "email": "identity@example.com",
                    "display_name": "Identity User",
                }
            ),
        ],
    )
    login = _login(SalesforceOAuth20Login, factory)
    payload = await login.auth_url()
    result = await login.exchange_and_identity(
        "auth-code-123", payload["state"]
    )

    _assert_token_post(factory)
    _assert_bearer_get(factory, USERINFO_URL)
    _assert_bearer_get(factory, IDENTITY_URL)
    assert result["sub"] == "005xx0000000002"
    assert result["email"] == "identity@example.com"
    assert result["name"] == "Identity User"
    assert result["raw"]["identity"]["user_id"] == "005xx0000000002"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_userinfo_error_falls_back_to_identity() -> (
    None
):
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[
            DummyResponse({"error": "boom"}, status=500),
            DummyResponse(
                {
                    "user_id": "005xx0000000003",
                    "email": "fallback@example.com",
                    "username": "fallback@example.com",
                }
            ),
        ],
    )
    login = _login(SalesforceOAuth20Login, factory)
    payload = await login.auth_url()
    result = await login.exchange_and_identity(
        "auth-code-123", payload["state"]
    )

    assert result["sub"] == "005xx0000000003"
    assert result["email"] == "fallback@example.com"
    assert result["name"] == "fallback@example.com"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_token_http_error_raises() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"error": "invalid_grant"}, status=400)],
    )
    login = _login(SalesforceOAuth20Login, factory)
    payload = await login.auth_url()
    with pytest.raises(FakeHTTPError):
        await login.exchange_and_identity("auth-code-123", payload["state"])


# --- SalesforceOAuth21Login ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_auth_url_discovers_endpoints() -> None:
    factory = DummyClientFactory(
        get_responses=[DummyResponse(dict(METADATA))],
    )
    login = _login(SalesforceOAuth21Login, factory, discovery_cache=False)
    payload = await login.auth_url()

    gets = factory.gets()
    assert len(gets) == 1
    assert gets[0]["url"] == DISCOVERY_URL
    assert gets[0]["headers"] == {"Accept": "application/json"}
    assert payload["url"].startswith(f"{AUTH_URL}?")
    params = parse_qs(urlsplit(payload["url"]).query)
    assert params["response_type"] == ["code"]
    assert params["code_challenge_method"] == ["S256"]
    assert params["state"] == [payload["state"]]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_exchange_returns_identity_from_id_token() -> None:
    id_token = _make_id_token(
        sub="005xx0000000001",
        email="user@example.com",
        name="Example User",
    )
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload(id_token=id_token))],
        get_responses=[DummyResponse(TEST_JWKS)],
    )
    login = _login(SalesforceOAuth21Login, factory)
    payload = await login.auth_url()
    result = await login.exchange_and_identity(
        "auth-code-123", payload["state"]
    )

    _assert_token_post(factory)
    gets = factory.gets()
    assert [c["url"] for c in gets] == [JWKS_URL]
    assert result["issuer"] == "salesforce-oauth21"
    assert result["sub"] == "005xx0000000001"
    assert result["email"] == "user@example.com"
    assert result["name"] == "Example User"
    assert result["raw"]["claims"]["sub"] == "005xx0000000001"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_exchange_falls_back_to_userinfo() -> None:
    id_token = _make_id_token(sub="005xx0000000001")
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload(id_token=id_token))],
        get_responses=[
            DummyResponse(TEST_JWKS),
            DummyResponse(
                {
                    "sub": "005xx0000000001",
                    "email": "userinfo@example.com",
                    "name": "Userinfo User",
                }
            ),
        ],
    )
    login = _login(SalesforceOAuth21Login, factory)
    payload = await login.auth_url()
    result = await login.exchange_and_identity(
        "auth-code-123", payload["state"]
    )

    _assert_bearer_get(factory, USERINFO_URL)
    assert result["sub"] == "005xx0000000001"
    assert result["email"] == "userinfo@example.com"
    assert result["name"] == "Userinfo User"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_exchange_missing_id_token_falls_back_to_userinfo() -> (
    None
):
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[
            DummyResponse(
                {
                    "sub": "005xx0000000004",
                    "email": "noid@example.com",
                    "name": "No Id Token",
                }
            ),
        ],
    )
    login = _login(SalesforceOAuth21Login, factory)
    payload = await login.auth_url()
    result = await login.exchange_and_identity(
        "auth-code-123", payload["state"]
    )

    # Current behavior: a missing id_token is swallowed and the UserInfo
    # endpoint supplies the identity instead of raising.
    assert result["raw"]["claims"] == {}
    assert result["sub"] == "005xx0000000004"
    assert result["email"] == "noid@example.com"
    assert result["name"] == "No Id Token"


# --- SalesforceOIDC10Login ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_exchange_returns_claims() -> None:
    id_token = _make_id_token(
        sub="005xx0000000001",
        email="user@example.com",
        name="Example User",
    )
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload(id_token=id_token))],
        get_responses=[DummyResponse(TEST_JWKS)],
    )
    login = _login(SalesforceOIDC10Login, factory)
    payload = await login.auth_url()
    # The OIDC request must carry the openid scope: without it Salesforce
    # returns no id_token, and this exchange would be impossible.
    params = parse_qs(urlsplit(payload["url"]).query)
    assert params["scope"] == ["openid refresh_token"]
    result = await login.exchange("auth-code-123", payload["state"])

    _assert_token_post(factory)
    gets = factory.gets()
    assert [c["url"] for c in gets] == [JWKS_URL]
    assert result["issuer"] == "salesforce-oidc"
    assert result["sub"] == "005xx0000000001"
    assert result["email"] == "user@example.com"
    assert result["name"] == "Example User"
    assert result["raw"]["claims"]["sub"] == "005xx0000000001"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_exchange_userinfo_fills_missing_email() -> None:
    id_token = _make_id_token(sub="005xx0000000001", name="Example User")
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload(id_token=id_token))],
        get_responses=[
            DummyResponse(TEST_JWKS),
            DummyResponse(
                {"email": "filled@example.com", "name": "Other Name"}
            ),
        ],
    )
    login = _login(SalesforceOIDC10Login, factory)
    payload = await login.auth_url()
    result = await login.exchange("auth-code-123", payload["state"])

    assert result["sub"] == "005xx0000000001"
    assert result["email"] == "filled@example.com"
    # Name already present in the claims is kept, not overwritten.
    assert result["name"] == "Example User"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_exchange_missing_id_token_raises() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[],
    )
    login = _login(SalesforceOIDC10Login, factory)
    payload = await login.auth_url()
    with pytest.raises(ValueError, match="no id_token in response"):
        await login.exchange("auth-code-123", payload["state"])


# --- SalesforceOAuth20AppClient ---


def _app_client20(factory, *, scope=None, aud=None):
    return SalesforceOAuth20AppClient(
        token_endpoint=TOKEN_URL,
        client_id=CLIENT_ID,
        user=USER,
        private_key_pem=SecretStr(TEST_PRIVATE_KEY_PEM),
        aud=aud,
        scope=scope,
        http_client_factory=factory,
    )


def _assert_jwt_bearer_post(factory, *, scope=None):
    posts = factory.posts()
    assert len(posts) == 1
    post = posts[0]
    assert post["url"] == TOKEN_URL
    assert post["headers"] == {"Accept": "application/json"}
    data = post["data"]
    assert data["grant_type"] == SalesforceOAuth20AppClient.JWT_GRANT
    assertion = jwt.decode(
        data["assertion"],
        jwt.algorithms.RSAAlgorithm.from_jwk(TEST_JWK),
        algorithms=["RS256"],
        audience=BASE_URL,
    )
    assert assertion["iss"] == CLIENT_ID
    assert assertion["sub"] == USER
    assert assertion["aud"] == BASE_URL
    assert assertion["exp"] - assertion["iat"] == 180
    if scope is None:
        assert "scope" not in data
    else:
        assert data["scope"] == scope
    return data


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_app_client_posts_jwt_bearer_assertion() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"access_token": "app-token"})],
    )
    client = _app_client20(factory)
    token = await client.access_token()

    assert token == "app-token"
    _assert_jwt_bearer_post(factory)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_app_client_sends_configured_scope() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"access_token": "app-token"})],
    )
    client = _app_client20(factory, scope="api refresh_token")
    token = await client.access_token()

    assert token == "app-token"
    _assert_jwt_bearer_post(factory, scope="api refresh_token")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_app_client_missing_access_token_raises() -> None:
    factory = DummyClientFactory(post_responses=[DummyResponse({})])
    client = _app_client20(factory)
    with pytest.raises(
        ValueError, match="access_token missing from Salesforce response"
    ):
        await client.access_token()


# NOTE: no end-to-end test for SalesforceOAuth21AppClient here. Its only
# key input is a JWK dict, and the inner client's _jwt_assertion passes
# that dict straight to jwt.encode, which current PyJWT rejects
# (TypeError: Expecting a PEM-formatted key). The delegation wiring itself
# is covered by the existing test_oauth21_app_client_unit.py; the JWK
# signing defect is tracked separately (see PR body).


# --- SalesforceOIDC10AppClient ---


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
    client = SalesforceOIDC10AppClient(
        issuer=BASE_URL,
        client_id=CLIENT_ID,
        user=USER,
        private_key_pem=SecretStr(TEST_PRIVATE_KEY_PEM),
        http_client_factory=factory,
    )

    token_one = await client.access_token()
    token_two = await client.access_token()

    assert token_one == "oidc-app-token"
    assert token_two == "oidc-app-token-2"
    # Discovery happens once; each token call still posts (no token cache).
    gets = factory.gets()
    assert len(gets) == 1
    assert gets[0]["url"] == DISCOVERY_URL
    posts = factory.posts()
    assert len(posts) == 2
    assert all(p["url"] == TOKEN_URL for p in posts)
    assert all(
        p["data"]["grant_type"] == SalesforceOAuth20AppClient.JWT_GRANT
        for p in posts
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_app_client_falls_back_to_default_token_endpoint() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"access_token": "oidc-app-token"})],
        get_responses=[DummyResponse({"issuer": BASE_URL})],
    )
    client = SalesforceOIDC10AppClient(
        issuer=BASE_URL,
        client_id=CLIENT_ID,
        user=USER,
        private_key_pem=SecretStr(TEST_PRIVATE_KEY_PEM),
        http_client_factory=factory,
    )

    token = await client.access_token()

    assert token == "oidc-app-token"
    posts = factory.posts()
    assert len(posts) == 1
    assert posts[0]["url"] == f"{BASE_URL}/services/oauth2/token"
