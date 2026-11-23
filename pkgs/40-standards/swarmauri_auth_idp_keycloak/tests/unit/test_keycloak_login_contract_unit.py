"""Offline contract tests for the Keycloak login flows (#6290).

Covers the primary public operation of each exported class, which the
existing unit tests only touch through construction, ``auth_url`` prefix
checks, and invalid-state failures:

- ``KeycloakOAuth20Login.exchange_and_identity``: realm issuer discovery
  (including reuse across ``auth_url`` and exchange), token exchange, and
  UserInfo mapping with the ``sub``/``id`` and ``name``/``given_name``
  fallbacks.
- ``KeycloakOAuth21Login.exchange_and_identity``: token exchange + ID
  token verification against a fake JWKS endpoint.
- ``KeycloakOIDC10Login.exchange``: token exchange + ID token
  verification, with the UserInfo fallback only when the claims are
  incomplete.
- ``KeycloakOAuth20AppClient.access_token``: client-credentials post
  (endpoint, form, basic auth) and the missing-``access_token`` failure.
- ``KeycloakOAuth21AppClient.access_token``: private-key JWT client
  assertion contents, and the secret-based fallback failure path.
- ``KeycloakOIDC10AppClient.access_token``: discovery through the fake
  client and the token post to the discovered endpoint.

Everything runs offline: a fake HTTP client serves discovery metadata,
token responses, UserInfo, and JWKS, and the ID tokens and client
assertions are signed with a throwaway RSA key generated for these tests.
No network access, credentials, or live Keycloak server are needed, and
nothing here proves interoperability with a production Keycloak realm.
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

from swarmauri_auth_idp_keycloak import (
    KeycloakOAuth20AppClient,
    KeycloakOAuth20Login,
    KeycloakOAuth21AppClient,
    KeycloakOAuth21Login,
    KeycloakOIDC10AppClient,
    KeycloakOIDC10Login,
)

ISSUER = "https://kc.example/realms/myrealm"
CLIENT_ID = "client"
TOKEN_URL = f"{ISSUER}/protocol/openid-connect/token"
AUTH_URL = f"{ISSUER}/protocol/openid-connect/auth"
USERINFO_URL = f"{ISSUER}/protocol/openid-connect/userinfo"
JWKS_URL = f"{ISSUER}/protocol/openid-connect/certs"
DISCOVERY_URL = f"{ISSUER}/.well-known/openid-configuration"

METADATA = {
    "issuer": ISSUER,
    "authorization_endpoint": AUTH_URL,
    "token_endpoint": TOKEN_URL,
    "userinfo_endpoint": USERINFO_URL,
    "jwks_uri": JWKS_URL,
}

# Throwaway RSA key for these tests only. The private half signs the ID
# tokens and client assertions below; the public half is served through
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
TEST_PRIVATE_JWK = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(_RSA_KEY))
TEST_PRIVATE_JWK.update(kid="test-key-1", use="sig", alg="RS256")


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
    sub: Optional[str] = "user-1",
    email: Optional[str] = None,
    name: Optional[str] = None,
    preferred_username: Optional[str] = None,
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
        issuer=ISSUER,
        client_id=CLIENT_ID,
        client_secret=SecretStr("secret"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"state-secret"),
        http_client_factory=factory,
    )
    if discovery_cache:
        instance.discovery_cache = dict(METADATA)
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


# --- KeycloakOAuth20Login ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_auth_url_discovers_realm_endpoints() -> None:
    factory = DummyClientFactory(
        get_responses=[DummyResponse(dict(METADATA))],
    )
    login = _login(KeycloakOAuth20Login, factory, discovery_cache=False)
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
async def test_oauth20_exchange_reuses_discovery_and_maps_userinfo() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[
            DummyResponse(dict(METADATA)),
            DummyResponse(
                {
                    "sub": "user-1",
                    "email": "user@example.com",
                    "name": "Example User",
                }
            ),
        ],
    )
    login = _login(KeycloakOAuth20Login, factory, discovery_cache=False)
    payload = await login.auth_url()
    result = await login.exchange_and_identity(
        "auth-code-123", payload["state"]
    )

    # Discovery is fetched once and reused by the exchange.
    discovery_gets = [c for c in factory.gets() if c["url"] == DISCOVERY_URL]
    assert len(discovery_gets) == 1
    _assert_token_post(factory)
    _assert_bearer_get(factory, USERINFO_URL)
    assert result["issuer"] == "keycloak-oauth20"
    assert result["sub"] == "user-1"
    assert result["email"] == "user@example.com"
    assert result["name"] == "Example User"
    assert result["raw"]["tokens"]["access_token"] == "access-123"
    assert result["raw"]["userinfo"]["email"] == "user@example.com"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_sub_and_name_fallbacks() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[
            DummyResponse(
                {
                    "id": "user-2",
                    "email": "fallback@example.com",
                    "given_name": "Gwen",
                }
            ),
        ],
    )
    login = _login(KeycloakOAuth20Login, factory)
    payload = await login.auth_url()
    result = await login.exchange_and_identity(
        "auth-code-123", payload["state"]
    )

    assert result["sub"] == "user-2"
    assert result["email"] == "fallback@example.com"
    assert result["name"] == "Gwen"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_without_userinfo_endpoint() -> None:
    metadata = {k: v for k, v in METADATA.items() if k != "userinfo_endpoint"}
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[],
    )
    login = _login(KeycloakOAuth20Login, factory)
    login.discovery_cache = dict(metadata)
    payload = await login.auth_url()
    result = await login.exchange_and_identity(
        "auth-code-123", payload["state"]
    )

    # Current behavior: no userinfo endpoint means an empty profile, so
    # the identity fields come back None instead of raising.
    assert factory.gets() == []
    assert result["sub"] is None
    assert result["email"] is None
    assert result["name"] is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_token_http_error_raises() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"error": "invalid_grant"}, status=400)],
    )
    login = _login(KeycloakOAuth20Login, factory)
    payload = await login.auth_url()
    with pytest.raises(FakeHTTPError):
        await login.exchange_and_identity("auth-code-123", payload["state"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_discovery_http_error_raises() -> None:
    factory = DummyClientFactory(
        get_responses=[DummyResponse({"error": "down"}, status=500)],
    )
    login = _login(KeycloakOAuth20Login, factory, discovery_cache=False)
    with pytest.raises(FakeHTTPError):
        await login.auth_url()


# --- KeycloakOAuth21Login ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_exchange_returns_identity_from_id_token() -> None:
    id_token = _make_id_token(
        sub="user-1",
        email="user@example.com",
        name="Example User",
    )
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload(id_token=id_token))],
        get_responses=[DummyResponse(TEST_JWKS)],
    )
    login = _login(KeycloakOAuth21Login, factory)
    payload = await login.auth_url()
    result = await login.exchange_and_identity(
        "auth-code-123", payload["state"]
    )

    _assert_token_post(factory)
    gets = factory.gets()
    assert [c["url"] for c in gets] == [JWKS_URL]
    assert result["issuer"] == "keycloak-oauth21"
    assert result["sub"] == "user-1"
    assert result["email"] == "user@example.com"
    assert result["name"] == "Example User"
    assert result["raw"]["claims"]["sub"] == "user-1"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_exchange_missing_id_token_raises() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[],
    )
    login = _login(KeycloakOAuth21Login, factory)
    payload = await login.auth_url()
    with pytest.raises(ValueError, match="no id_token in response"):
        await login.exchange_and_identity("auth-code-123", payload["state"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_exchange_missing_sub_raises() -> None:
    id_token = _make_id_token(sub=None, email="nosub@example.com")
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload(id_token=id_token))],
        get_responses=[DummyResponse(TEST_JWKS)],
    )
    login = _login(KeycloakOAuth21Login, factory)
    payload = await login.auth_url()
    # Current behavior: the claims decode fine, then the missing "sub"
    # lookup raises KeyError instead of a friendlier error.
    with pytest.raises(KeyError, match="sub"):
        await login.exchange_and_identity("auth-code-123", payload["state"])


# --- KeycloakOIDC10Login ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_exchange_returns_claims() -> None:
    id_token = _make_id_token(
        sub="user-1",
        email="user@example.com",
        name="Example User",
    )
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload(id_token=id_token))],
        get_responses=[DummyResponse(TEST_JWKS)],
    )
    login = _login(KeycloakOIDC10Login, factory)
    payload = await login.auth_url()
    result = await login.exchange("auth-code-123", payload["state"])

    _assert_token_post(factory)
    gets = factory.gets()
    assert [c["url"] for c in gets] == [JWKS_URL]
    assert result["issuer"] == "keycloak-oidc"
    assert result["sub"] == "user-1"
    assert result["email"] == "user@example.com"
    assert result["name"] == "Example User"
    assert result["raw"]["claims"]["sub"] == "user-1"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_exchange_userinfo_fills_missing_email_and_name() -> None:
    id_token = _make_id_token(sub="user-1")
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload(id_token=id_token))],
        get_responses=[
            DummyResponse(TEST_JWKS),
            DummyResponse(
                {"email": "filled@example.com", "given_name": "Faye"}
            ),
        ],
    )
    login = _login(KeycloakOIDC10Login, factory)
    payload = await login.auth_url()
    result = await login.exchange("auth-code-123", payload["state"])

    assert result["sub"] == "user-1"
    assert result["email"] == "filled@example.com"
    assert result["name"] == "Faye"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_exchange_missing_id_token_raises() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[],
    )
    login = _login(KeycloakOIDC10Login, factory)
    payload = await login.auth_url()
    with pytest.raises(ValueError, match="no id_token in response"):
        await login.exchange("auth-code-123", payload["state"])


# --- KeycloakOAuth20AppClient ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_app_client_posts_client_credentials() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"access_token": "app-token"})],
    )
    client = KeycloakOAuth20AppClient(
        issuer=ISSUER,
        client_id=CLIENT_ID,
        client_secret=SecretStr("secret"),
        http_client_factory=factory,
    )
    token = await client.access_token(scope="api")

    assert token == "app-token"
    posts = factory.posts()
    assert len(posts) == 1
    post = posts[0]
    assert post["url"] == TOKEN_URL
    assert post["headers"] == {"Accept": "application/json"}
    assert post["data"] == {
        "grant_type": "client_credentials",
        "scope": "api",
    }
    assert post["auth"] == (CLIENT_ID, "secret")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_app_client_missing_access_token_raises() -> None:
    factory = DummyClientFactory(post_responses=[DummyResponse({})])
    client = KeycloakOAuth20AppClient(
        issuer=ISSUER,
        client_id=CLIENT_ID,
        client_secret=SecretStr("secret"),
        http_client_factory=factory,
    )
    with pytest.raises(
        ValueError, match="access_token missing from Keycloak response"
    ):
        await client.access_token()


# --- KeycloakOAuth21AppClient ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_app_client_posts_jwt_assertion() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"access_token": "app-token-21"})],
    )
    client = KeycloakOAuth21AppClient(
        issuer=ISSUER,
        client_id=CLIENT_ID,
        private_key_jwk=dict(TEST_PRIVATE_JWK),
        http_client_factory=factory,
    )
    token = await client.access_token()

    assert token == "app-token-21"
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
    assert assertion["jti"].startswith(f"{CLIENT_ID}-")
    assert jwt.get_unverified_header(data["client_assertion"])["kid"] == (
        "test-key-1"
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_app_client_missing_access_token_raises() -> None:
    factory = DummyClientFactory(post_responses=[DummyResponse({})])
    client = KeycloakOAuth21AppClient(
        issuer=ISSUER,
        client_id=CLIENT_ID,
        client_secret=SecretStr("secret"),
        http_client_factory=factory,
    )
    with pytest.raises(
        ValueError, match="access_token missing from Keycloak response"
    ):
        await client.access_token()


# --- KeycloakOIDC10AppClient ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_app_client_discovers_token_endpoint() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"access_token": "oidc-app-token"})],
        get_responses=[DummyResponse(dict(METADATA))],
    )
    client = KeycloakOIDC10AppClient(
        issuer=ISSUER,
        client_id=CLIENT_ID,
        client_secret=SecretStr("secret"),
        http_client_factory=factory,
    )
    token = await client.access_token()

    assert token == "oidc-app-token"
    gets = factory.gets()
    assert len(gets) == 1
    assert gets[0]["url"] == DISCOVERY_URL
    assert gets[0]["headers"] == {"Accept": "application/json"}
    posts = factory.posts()
    assert len(posts) == 1
    assert posts[0]["url"] == TOKEN_URL
    assert posts[0]["auth"] == (CLIENT_ID, "secret")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc_app_client_discovery_without_token_endpoint_raises() -> (
    None
):
    factory = DummyClientFactory(
        post_responses=[],
        get_responses=[DummyResponse({"issuer": ISSUER})],
    )
    client = KeycloakOIDC10AppClient(
        issuer=ISSUER,
        client_id=CLIENT_ID,
        client_secret=SecretStr("secret"),
        http_client_factory=factory,
    )
    # Current behavior: a discovery document without token_endpoint raises
    # a bare KeyError instead of a friendlier error.
    with pytest.raises(KeyError, match="token_endpoint"):
        await client.access_token()
