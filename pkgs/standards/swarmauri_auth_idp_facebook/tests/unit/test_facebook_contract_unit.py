"""Deterministic provider contract tests for Facebook logins/app clients.

Every test runs offline against a fake HTTP client: no network access,
no environment secrets, no paid services. The fake client records each
request (URL, method, headers, form fields) so the tests assert the
provider contract, not just construction or return types.

Class-to-test checklist (issue #6280):
- FacebookOAuth20AppClient: test_oauth20_app_client_* (token fetch,
  cache, missing token, HTTP error)
- FacebookOAuth21AppClient: test_oauth21_app_client_access_token_*
  (delegates to the OAuth 2.0 client over HTTP)
- FacebookOIDC10AppClient: test_oidc10_app_client_access_token_*
  (no client-credentials OIDC flow exists)
- FacebookOAuth20Login: test_oauth20_login_exchange_* (token POST +
  Graph profile GET, failure paths)
- FacebookOAuth21Login: test_oauth21_login_exchange_* (ID-token path
  with local JWKS, profile fallback)
- FacebookOIDC10Login: test_oidc10_login_exchange_* (discovery, token
  POST, JWKS ID-token decode, userinfo fallback, failure paths)
"""

import base64
import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from pydantic import SecretStr

from swarmauri_auth_idp_facebook import (
    FacebookOAuth20AppClient,
    FacebookOAuth21AppClient,
    FacebookOIDC10AppClient,
    FacebookOAuth20Login,
    FacebookOAuth21Login,
    FacebookOIDC10Login,
)


class FakeHTTPError(Exception):
    """Stands in for a provider HTTP error (raise_for_status)."""


class FakeResponse:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise FakeHTTPError(f"HTTP {self.status_code}")


class FakeHTTPClient:
    """Fake RetryingAsyncClient: records calls, serves canned JSON."""

    def __init__(self, routes):
        self.routes = routes
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def get_retry(self, url, **kwargs):
        self.calls.append(("GET", url, kwargs.get("headers", {}), None))
        return self._respond("GET", url)

    async def post_retry(self, url, **kwargs):
        self.calls.append(
            ("POST", url, kwargs.get("headers", {}), kwargs.get("data"))
        )
        return self._respond("POST", url)

    def _respond(self, method, url):
        route = self.routes.get((method, url))
        if route is None:
            raise AssertionError(f"unexpected {method} {url}")
        if isinstance(route, Exception):
            raise route
        if isinstance(route, FakeResponse):
            route.raise_for_status()
            return route
        return FakeResponse(route)


class FakeHTTPClientFactory:
    """Callable factory object (not a plain function: plain functions
    bind as methods when assigned on the class)."""

    def __init__(self, client):
        self.client = client

    def __call__(self):
        return self.client


def _b64url_int(value: int) -> str:
    raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


@pytest.fixture(scope="module")
def rsa_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(scope="module")
def jwks(rsa_key):
    numbers = rsa_key.public_key().public_numbers()
    return {
        "keys": [
            {
                "kty": "RSA",
                "kid": "test-key",
                "use": "sig",
                "alg": "RS256",
                "n": _b64url_int(numbers.n),
                "e": _b64url_int(numbers.e),
            }
        ]
    }


def _mint_id_token(rsa_key, **overrides):
    now = int(time.time())
    payload = {
        "iss": "https://www.facebook.com",
        "aud": "app-id",
        "sub": "user-1",
        "email": "user@example.com",
        "name": "Example User",
        "exp": now + 600,
        "iat": now,
    }
    payload.update(overrides)
    return jwt.encode(
        payload, rsa_key, algorithm="RS256", headers={"kid": "test-key"}
    )


TOKEN_URL = "https://graph.facebook.com/v19.0/oauth/access_token"
PROFILE_URL = "https://graph.facebook.com/v19.0/me?fields=id,name,email"
JWKS_URL = "https://www.facebook.com/.well-known/oauth/openid/jwks/"
DISCOVERY_URL = "https://www.facebook.com/.well-known/openid-configuration"
AUTH_URL_BASE = "https://www.facebook.com/v19.0/dialog/oauth"


def _login_fixture(cls):
    return cls(
        client_id="app-id",
        client_secret=SecretStr("app-secret"),
        redirect_uri="https://app.example.com/callback",
        state_secret=b"state-secret",
    )


# --- App clients ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_app_client_access_token_posts_client_credentials():
    fake = FakeHTTPClient(
        {
            ("POST", TOKEN_URL): {
                "access_token": "app-token",
                "token_type": "bearer",
                "expires_in": 3600,
            }
        }
    )
    client = FacebookOAuth20AppClient(
        client_id="app-id",
        client_secret=SecretStr("app-secret"),
        graph_base="https://graph.facebook.com",
        version="v19.0",
    )
    client._http_client_factory = lambda: fake

    token = await client.access_token()
    assert token == "app-token"
    # Second call is served from cache: no second HTTP request.
    assert await client.access_token() == "app-token"
    assert len(fake.calls) == 1

    method, url, headers, data = fake.calls[0]
    assert method == "POST"
    assert url == TOKEN_URL
    assert headers.get("Accept") == "application/json"
    assert data == {
        "grant_type": "client_credentials",
        "client_id": "app-id",
        "client_secret": "app-secret",
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_app_client_access_token_missing_token():
    fake = FakeHTTPClient({("POST", TOKEN_URL): {"expires_in": 60}})
    client = FacebookOAuth20AppClient(
        client_id="app-id",
        client_secret=SecretStr("app-secret"),
    )
    client._http_client_factory = lambda: fake
    with pytest.raises(ValueError):
        await client.access_token()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_app_client_access_token_http_error():
    fake = FakeHTTPClient(
        {("POST", TOKEN_URL): FakeHTTPError("provider unavailable")}
    )
    client = FacebookOAuth20AppClient(
        client_id="app-id",
        client_secret=SecretStr("app-secret"),
    )
    client._http_client_factory = lambda: fake
    with pytest.raises(FakeHTTPError):
        await client.access_token()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_app_client_access_token_delegates_over_http(
    monkeypatch: pytest.MonkeyPatch,
):
    fake = FakeHTTPClient(
        {
            ("POST", TOKEN_URL): {
                "access_token": "app-token-21",
                "token_type": "bearer",
                "expires_in": 3600,
            }
        }
    )
    # The OAuth 2.1 client builds its own OAuth 2.0 client internally,
    # so the fake factory is installed on that class for this test.
    monkeypatch.setattr(
        FacebookOAuth20AppClient,
        "_http_client_factory",
        FakeHTTPClientFactory(fake),
    )
    client = FacebookOAuth21AppClient(
        client_id="app-id",
        client_secret=SecretStr("app-secret"),
    )
    assert await client.access_token() == "app-token-21"
    assert len(fake.calls) == 1
    method, url, _headers, data = fake.calls[0]
    assert (method, url) == ("POST", TOKEN_URL)
    assert data["grant_type"] == "client_credentials"
    assert data["client_id"] == "app-id"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc10_app_client_access_token_not_supported():
    client = FacebookOIDC10AppClient()
    with pytest.raises(NotImplementedError):
        await client.access_token()


# --- OAuth 2.0 login ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_login_exchange_posts_token_and_fetches_profile():
    fake = FakeHTTPClient(
        {
            ("POST", TOKEN_URL): {
                "access_token": "user-token",
                "token_type": "bearer",
                "expires_in": 3600,
            },
            ("GET", PROFILE_URL): {
                "id": "123",
                "name": "Example User",
                "email": "user@example.com",
            },
        }
    )
    login = _login_fixture(FacebookOAuth20Login)
    login._http_client_factory = lambda: fake

    payload = await login.auth_url()
    assert payload["url"].startswith(f"{AUTH_URL_BASE}?")
    assert "client_id=app-id" in payload["url"]
    assert "code_challenge_method=S256" in payload["url"]

    result = await login.exchange_and_identity("auth-code", payload["state"])
    assert result["issuer"] == "facebook-oauth20"
    assert result["sub"] == "123"
    assert result["email"] == "user@example.com"
    assert result["name"] == "Example User"
    assert result["tokens"]["access_token"] == "user-token"

    assert len(fake.calls) == 2
    method, url, _headers, data = fake.calls[0]
    assert (method, url) == ("POST", TOKEN_URL)
    assert data["grant_type"] == "authorization_code"
    assert data["code"] == "auth-code"
    assert data["redirect_uri"] == "https://app.example.com/callback"
    assert data["client_id"] == "app-id"
    assert data["client_secret"] == "app-secret"
    assert data["code_verifier"]

    method, url, headers, _data = fake.calls[1]
    assert (method, url) == ("GET", PROFILE_URL)
    assert headers["Authorization"] == "Bearer user-token"
    assert headers["Accept"] == "application/json"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_login_exchange_token_http_error():
    fake = FakeHTTPClient(
        {("POST", TOKEN_URL): FakeHTTPError("provider unavailable")}
    )
    login = _login_fixture(FacebookOAuth20Login)
    login._http_client_factory = lambda: fake
    payload = await login.auth_url()
    with pytest.raises(FakeHTTPError):
        await login.exchange_and_identity("auth-code", payload["state"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_login_profile_missing_id_records_current_behavior():
    fake = FakeHTTPClient(
        {
            ("POST", TOKEN_URL): {"access_token": "user-token"},
            ("GET", PROFILE_URL): {"email": "user@example.com"},
        }
    )
    login = _login_fixture(FacebookOAuth20Login)
    login._http_client_factory = lambda: fake
    payload = await login.auth_url()
    result = await login.exchange_and_identity("auth-code", payload["state"])
    # Current behavior: a profile without `id` yields no subject.
    assert result["sub"] is None
    assert result["email"] == "user@example.com"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_uses_configured_auth_and_graph_bases():
    login = FacebookOAuth20Login(
        client_id="app-id",
        client_secret=SecretStr("app-secret"),
        redirect_uri="https://app.example.com/callback",
        state_secret=b"state-secret",
        auth_base="https://www.facebook.com/v20.0",
        graph_base="https://graph.facebook.com/v20.0",
    )
    payload = await login.auth_url()
    assert payload["url"].startswith(
        "https://www.facebook.com/v20.0/dialog/oauth?"
    )
    assert (
        login._token_endpoint()
        == "https://graph.facebook.com/v20.0/oauth/access_token"
    )
    assert (
        login._graph_me_endpoint()
        == "https://graph.facebook.com/v20.0/me?fields=id,name,email"
    )


# --- OAuth 2.1 login ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_login_exchange_uses_id_token(rsa_key, jwks):
    id_token = _mint_id_token(rsa_key)
    fake = FakeHTTPClient(
        {
            ("POST", TOKEN_URL): {
                "access_token": "user-token",
                "id_token": id_token,
            },
            ("GET", JWKS_URL): jwks,
        }
    )
    login = _login_fixture(FacebookOAuth21Login)
    login._http_client_factory = lambda: fake
    payload = await login.auth_url()
    result = await login.exchange_and_identity("auth-code", payload["state"])
    assert result["issuer"] == "facebook-oauth21"
    assert result["sub"] == "user-1"
    assert result["email"] == "user@example.com"
    assert result["name"] == "Example User"
    assert result["claims"]["iss"] == "https://www.facebook.com"

    methods_urls = [(c[0], c[1]) for c in fake.calls]
    assert ("POST", TOKEN_URL) in methods_urls
    assert ("GET", JWKS_URL) in methods_urls


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_login_exchange_falls_back_to_profile():
    fake = FakeHTTPClient(
        {
            ("POST", TOKEN_URL): {"access_token": "user-token"},
            ("GET", PROFILE_URL): {
                "id": "321",
                "name": "Fallback User",
                "email": "fallback@example.com",
            },
        }
    )
    login = _login_fixture(FacebookOAuth21Login)
    login._http_client_factory = lambda: fake
    payload = await login.auth_url()
    result = await login.exchange_and_identity("auth-code", payload["state"])
    assert result["issuer"] == "facebook-oauth21"
    assert result["sub"] == "321"
    assert result["name"] == "Fallback User"


# --- OIDC 1.0 login ---


def _oidc_metadata(**overrides):
    metadata = {
        "authorization_endpoint": AUTH_URL_BASE,
        "token_endpoint": TOKEN_URL,
        "jwks_uri": JWKS_URL,
        "issuer": "https://www.facebook.com",
    }
    metadata.update(overrides)
    return metadata


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc10_login_exchange_decodes_id_token(rsa_key, jwks):
    id_token = _mint_id_token(rsa_key)
    fake = FakeHTTPClient(
        {
            ("GET", DISCOVERY_URL): _oidc_metadata(),
            ("POST", TOKEN_URL): {
                "access_token": "user-token",
                "id_token": id_token,
            },
            ("GET", JWKS_URL): jwks,
        }
    )
    login = _login_fixture(FacebookOIDC10Login)
    login._http_client_factory = lambda: fake

    payload = await login.auth_url()
    assert payload["url"].startswith(f"{AUTH_URL_BASE}?")
    result = await login.exchange("auth-code", payload["state"])
    assert result["issuer"] == "facebook-oidc10"
    assert result["sub"] == "user-1"
    assert result["email"] == "user@example.com"
    assert result["name"] == "Example User"
    assert result["tokens"]["access_token"] == "user-token"

    post_calls = [c for c in fake.calls if c[0] == "POST"]
    assert len(post_calls) == 1
    _method, url, _headers, data = post_calls[0]
    assert url == TOKEN_URL
    assert data["grant_type"] == "authorization_code"
    assert data["code"] == "auth-code"
    assert data["client_secret"] == "app-secret"
    assert data["code_verifier"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc10_login_exchange_uses_userinfo_when_claims_incomplete(
    rsa_key, jwks
):
    id_token = _mint_id_token(rsa_key, email=None, name=None)
    userinfo_url = "https://graph.facebook.com/me?fields=id,name,email"
    fake = FakeHTTPClient(
        {
            ("GET", DISCOVERY_URL): _oidc_metadata(
                userinfo_endpoint=userinfo_url
            ),
            ("POST", TOKEN_URL): {
                "access_token": "user-token",
                "id_token": id_token,
            },
            ("GET", JWKS_URL): jwks,
            ("GET", userinfo_url): {
                "email": "userinfo@example.com",
                "name": "Userinfo User",
            },
        }
    )
    login = _login_fixture(FacebookOIDC10Login)
    login._http_client_factory = lambda: fake
    payload = await login.auth_url()
    result = await login.exchange("auth-code", payload["state"])
    assert result["email"] == "userinfo@example.com"
    assert result["name"] == "Userinfo User"
    userinfo_calls = [
        c for c in fake.calls if c[0] == "GET" and c[1] == userinfo_url
    ]
    assert len(userinfo_calls) == 1
    assert (
        userinfo_calls[0][2]["Authorization"] == "Bearer user-token"
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc10_login_exchange_missing_id_token():
    fake = FakeHTTPClient(
        {
            ("GET", DISCOVERY_URL): _oidc_metadata(),
            ("POST", TOKEN_URL): {"access_token": "user-token"},
        }
    )
    login = _login_fixture(FacebookOIDC10Login)
    login._http_client_factory = lambda: fake
    payload = await login.auth_url()
    with pytest.raises(ValueError, match="no id_token in response"):
        await login.exchange("auth-code", payload["state"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc10_login_exchange_token_http_error():
    fake = FakeHTTPClient(
        {
            ("GET", DISCOVERY_URL): _oidc_metadata(),
            ("POST", TOKEN_URL): FakeHTTPError("provider unavailable"),
        }
    )
    login = _login_fixture(FacebookOIDC10Login)
    login._http_client_factory = lambda: fake
    payload = await login.auth_url()
    with pytest.raises(FakeHTTPError):
        await login.exchange("auth-code", payload["state"])
