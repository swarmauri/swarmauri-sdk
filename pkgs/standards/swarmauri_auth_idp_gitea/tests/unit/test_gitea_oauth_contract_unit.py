"""Offline contract tests for the Gitea login and app-client flows (#6282).

Covers the primary public operation of each exported class, which the
existing unit tests only touch through resource/type checks, ``auth_url``
prefix checks, invalid-state failures, and token-cache behavior:

- ``GiteaOAuth20Login.auth_url``: self-hosted authorization endpoint and
  default ``read:user`` scope.
- ``GiteaOAuth20Login.exchange_and_identity``: token exchange + ``/user``
  mapping, including the ``/user/emails`` primary-email fallback, the
  ``full_name``/``username``/``login`` fallback chain, and a custom
  ``api_base``.
- ``GiteaOAuth21Login.exchange_and_identity``: same profile flow as the
  OAuth 2.0 login (this class reuses the OAuth mixin, not discovery).
- ``GiteaOIDC10Login.exchange``: token exchange + ID token verification,
  with the ``preferred_username`` fallback, the ``"Unknown"`` name rule,
  and the UserInfo fallback only when email is missing or the name is
  unknown.
- ``auth_url`` without preset discovery: issuer discovery through the
  fake client.
- ``GiteaOAuth20AppClient.access_token``: client-credentials POST (form,
  basic auth, scope) and cache reuse.
- ``GiteaOAuth21AppClient.access_token``: secret-auth and private-key
  client-assertion paths.
- ``GiteaOIDC10AppClient.access_token``: discovery-driven token endpoint.

Everything runs offline: a fake HTTP client serves discovery metadata,
token responses, UserInfo, and JWKS, and the ID tokens and client
assertions are signed with a throwaway RSA key generated for these tests.
No network access, credentials, or live Gitea account are needed, and
nothing here proves interoperability with Gitea's production service.
"""

from __future__ import annotations

import json
import time
from typing import Any
from urllib.parse import parse_qs, urlsplit

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_gitea import (
    GiteaOAuth20AppClient,
    GiteaOAuth20Login,
    GiteaOAuth21AppClient,
    GiteaOAuth21Login,
    GiteaOIDC10AppClient,
    GiteaOIDC10Login,
)
from swarmauri_base.auth_idp import verify_state

BASE_URL = "https://gitea.example"
ISSUER = "https://gitea.example"
CLIENT_ID = "client"
STATE_SECRET = b"0123456789abcdef0123456789abcdef"

METADATA = {
    "issuer": ISSUER,
    "authorization_endpoint": f"{BASE_URL}/login/oauth/authorize",
    "token_endpoint": f"{BASE_URL}/login/oauth/access_token",
    "userinfo_endpoint": f"{BASE_URL}/api/v1/user",
    "jwks_uri": f"{BASE_URL}/login/oauth/jwks",
}

API_USER_ENDPOINT = f"{BASE_URL}/api/v1/user"
TOKEN_ENDPOINT = f"{BASE_URL}/login/oauth/access_token"
DISCOVERY_ENDPOINT = f"{ISSUER}/.well-known/openid-configuration"

# Throwaway RSA key for these tests only. The private half signs the ID
# tokens and the OAuth 2.1 client assertions below; the public half is
# served through the fake JWKS endpoint. It is never used outside this
# file.
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
TEST_PRIVATE_JWK.update(kid="test-key-2", use="sig", alg="RS256")


class FakeHTTPError(Exception):
    """Raised by the fake client when a canned response carries an
    error status."""


class DummyResponse:
    def __init__(self, payload: dict[str, Any] | list, status: int = 200):
        self._payload = payload
        self.status = status

    def raise_for_status(self) -> None:
        if self.status >= 400:
            raise FakeHTTPError(f"HTTP {self.status}")

    def json(self) -> dict[str, Any] | list:
        return self._payload


class DummyClient:
    def __init__(self, factory: DummyClientFactory):
        self._factory = factory

    async def __aenter__(self) -> DummyClient:  # noqa: PYI034
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False

    async def post_retry(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        auth: Any | None = None,
        headers: dict[str, str] | None = None,
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
        headers: dict[str, str] | None = None,
    ) -> DummyResponse:
        self._factory.calls.append(
            {"method": "GET", "url": url, "headers": dict(headers or {})}
        )
        return self._factory.get_responses.pop(0)


class DummyClientFactory:
    def __init__(
        self,
        *,
        post_responses: list[DummyResponse] | None = None,
        get_responses: list[DummyResponse] | None = None,
    ):
        self.post_responses = list(post_responses or [])
        self.get_responses = list(get_responses or [])
        self.calls: list[dict[str, Any]] = []

    def __call__(self) -> DummyClient:
        return DummyClient(self)

    def posts(self) -> list[dict[str, Any]]:
        return [c for c in self.calls if c["method"] == "POST"]

    def gets(self) -> list[dict[str, Any]]:
        return [c for c in self.calls if c["method"] == "GET"]


def _make_id_token(
    *,
    sub: str,
    email: str | None = None,
    name: str | None = None,
    preferred_username: str | None = None,
) -> str:
    now = int(time.time())
    claims: dict[str, Any] = {
        "sub": sub,
        "iss": ISSUER,
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


def _login(cls, factory, *, discovery_cache=True, api_base=None):
    # Gitea classes take the HTTP factory as a private attribute, not a
    # constructor field; discovery is a private attribute too.
    kwargs: dict[str, Any] = {
        "client_id": CLIENT_ID,
        "client_secret": SecretStr("secret"),
    }
    if cls in (GiteaOIDC10Login, GiteaOIDC10AppClient):
        kwargs["issuer"] = ISSUER
    else:
        kwargs["base_url"] = BASE_URL
    if cls in (GiteaOAuth20Login, GiteaOAuth21Login, GiteaOIDC10Login):
        kwargs["redirect_uri"] = "https://example.com/callback"
        kwargs["state_secret"] = SecretBytes(STATE_SECRET)
    if api_base is not None:
        kwargs["api_base"] = api_base
    instance = cls(**kwargs)
    instance._http_client_factory = factory
    if discovery_cache and hasattr(instance, "_discovery"):
        instance._discovery = dict(METADATA)
    return instance


def _token_payload(*, id_token: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "access_token": "access-123",
        "token_type": "Bearer",
        "expires_in": 3600,
    }
    if id_token is not None:
        payload["id_token"] = id_token
    return payload


def _assert_token_post(factory, *, code="auth-code-123") -> dict[str, Any]:
    posts = factory.posts()
    assert len(posts) == 1
    post = posts[0]
    assert post["url"] == TOKEN_ENDPOINT
    assert post["headers"] == {"Accept": "application/json"}
    data = post["data"]
    assert data["grant_type"] == "authorization_code"
    assert data["code"] == code
    assert data["redirect_uri"] == "https://example.com/callback"
    assert data["client_id"] == CLIENT_ID
    assert data["client_secret"] == "secret"
    assert data["code_verifier"]
    return data


def _state_payload(state: str) -> dict[str, Any]:
    return verify_state(STATE_SECRET, state)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_auth_url_uses_base_url_and_scope() -> None:
    login = _login(GiteaOAuth20Login, DummyClientFactory())

    auth = await login.auth_url()

    assert auth["url"].startswith(f"{BASE_URL}/login/oauth/authorize?")
    parsed = parse_qs(urlsplit(auth["url"]).query)
    assert parsed["response_type"] == ["code"]
    assert parsed["client_id"] == [CLIENT_ID]
    assert parsed["redirect_uri"] == ["https://example.com/callback"]
    assert parsed["scope"] == ["read:user"]
    assert parsed["code_challenge_method"] == ["S256"]
    assert parsed["code_challenge"]
    assert parsed["state"] == [auth["state"]]
    payload = _state_payload(auth["state"])
    assert payload["verifier"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_returns_identity_from_user() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[
            DummyResponse(
                {"id": 42, "email": "ada@example.com", "full_name": "Ada"}
            )
        ],
    )
    login = _login(GiteaOAuth20Login, factory)
    auth = await login.auth_url()

    identity = await login.exchange_and_identity(
        "auth-code-123", auth["state"]
    )

    assert identity["issuer"] == "gitea-oauth2"
    assert identity["sub"] == "42"
    assert identity["email"] == "ada@example.com"
    assert identity["name"] == "Ada"
    assert identity["raw"]["tokens"]["access_token"] == "access-123"
    assert identity["raw"]["user"]["id"] == 42
    data = _assert_token_post(factory)
    assert data["code_verifier"] == _state_payload(auth["state"])["verifier"]
    gets = factory.gets()
    assert len(gets) == 1
    assert gets[0]["url"] == API_USER_ENDPOINT
    assert gets[0]["headers"] == {
        "Authorization": "Bearer access-123",
        "Accept": "application/json",
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_falls_back_to_primary_email() -> None:
    # The profile has no email, so the mixin consults /user/emails and
    # picks the primary verified address; the name falls back to login.
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[
            DummyResponse({"id": 7, "login": "bo"}),
            DummyResponse(
                [
                    {
                        "email": "other@example.com",
                        "primary": False,
                        "verified": True,
                    },
                    {
                        "email": "bo@example.com",
                        "primary": True,
                        "verified": True,
                    },
                ]
            ),
        ],
    )
    login = _login(GiteaOAuth20Login, factory)
    auth = await login.auth_url()

    identity = await login.exchange_and_identity(
        "auth-code-123", auth["state"]
    )

    assert identity["sub"] == "7"
    assert identity["email"] == "bo@example.com"
    assert identity["name"] == "bo"
    assert [g["url"] for g in factory.gets()] == [
        API_USER_ENDPOINT,
        f"{BASE_URL}/api/v1/user/emails",
    ]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_uses_custom_api_base() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[
            DummyResponse(
                {"id": 9, "email": "cy@example.com", "username": "cy"}
            )
        ],
    )
    login = _login(
        GiteaOAuth20Login, factory, api_base="https://api.gitea.example"
    )
    auth = await login.auth_url()

    identity = await login.exchange_and_identity(
        "auth-code-123", auth["state"]
    )

    assert identity["sub"] == "9"
    assert identity["name"] == "cy"
    gets = factory.gets()
    assert len(gets) == 1
    assert gets[0]["url"] == "https://api.gitea.example/user"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_exchange_returns_identity_from_user() -> None:
    # Gitea's OAuth 2.1 login reuses the OAuth mixin (no discovery, no
    # ID token); only the issuer label differs from OAuth 2.0.
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[
            DummyResponse(
                {"id": 11, "email": "di@example.com", "username": "di"}
            )
        ],
    )
    login = _login(GiteaOAuth21Login, factory)
    auth = await login.auth_url()

    identity = await login.exchange_and_identity(
        "auth-code-123", auth["state"]
    )

    assert identity["issuer"] == "gitea-oauth21"
    assert identity["sub"] == "11"
    assert identity["email"] == "di@example.com"
    assert identity["name"] == "di"
    _assert_token_post(factory)
    assert factory.gets()[0]["url"] == API_USER_ENDPOINT


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_propagates_provider_http_error() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"error": "server_error"}, status=500)],
    )
    login = _login(GiteaOAuth20Login, factory)
    auth = await login.auth_url()

    with pytest.raises(FakeHTTPError):
        await login.exchange_and_identity("auth-code-123", auth["state"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_missing_access_token() -> None:
    # Current behavior: the token response is used without a presence
    # check, so a response without access_token fails on the lookup.
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"token_type": "Bearer"})],
    )
    login = _login(GiteaOAuth20Login, factory)
    auth = await login.auth_url()

    with pytest.raises(KeyError):
        await login.exchange_and_identity("auth-code-123", auth["state"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc10_auth_url_uses_discovery() -> None:
    login = _login(GiteaOIDC10Login, DummyClientFactory())

    auth = await login.auth_url()

    assert auth["url"].startswith(f"{METADATA['authorization_endpoint']}?")
    parsed = parse_qs(urlsplit(auth["url"]).query)
    assert parsed["response_type"] == ["code"]
    assert parsed["scope"] == ["openid email profile"]
    assert parsed["code_challenge_method"] == ["S256"]
    assert parsed["code_challenge"]
    payload = _state_payload(auth["state"])
    assert payload["verifier"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc10_exchange_returns_identity_from_id_token() -> None:
    factory = DummyClientFactory(
        get_responses=[DummyResponse(TEST_JWKS)],
    )
    login = _login(GiteaOIDC10Login, factory)
    auth = await login.auth_url()
    id_token = _make_id_token(
        sub="gitea-456", email="cy@example.com", name="Cy"
    )
    factory.post_responses = [DummyResponse(_token_payload(id_token=id_token))]

    identity = await login.exchange("auth-code-123", auth["state"])

    assert identity["issuer"] == "gitea-oidc"
    assert identity["sub"] == "gitea-456"
    assert identity["email"] == "cy@example.com"
    assert identity["name"] == "Cy"
    assert identity["raw"]["tokens"]["access_token"] == "access-123"
    _assert_token_post(factory)
    gets = factory.gets()
    assert len(gets) == 1
    assert gets[0]["url"] == METADATA["jwks_uri"]
    assert gets[0]["headers"] == {"Accept": "application/json"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc10_exchange_falls_back_to_preferred_username() -> None:
    # Claims carry email + preferred_username but no name; the name is
    # resolved (not "Unknown"), so no UserInfo lookup happens.
    factory = DummyClientFactory(
        get_responses=[DummyResponse(TEST_JWKS)],
    )
    login = _login(GiteaOIDC10Login, factory)
    auth = await login.auth_url()
    id_token = _make_id_token(
        sub="gitea-789",
        email="bo@example.com",
        preferred_username="bo",
    )
    factory.post_responses = [DummyResponse(_token_payload(id_token=id_token))]

    identity = await login.exchange("auth-code-123", auth["state"])

    assert identity["sub"] == "gitea-789"
    assert identity["email"] == "bo@example.com"
    assert identity["name"] == "bo"
    assert [g["url"] for g in factory.gets()] == [METADATA["jwks_uri"]]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc10_exchange_uses_userinfo_when_name_unknown() -> None:
    # Claims carry email but no name, so the name resolves to "Unknown"
    # and the UserInfo lookup supplies the real name.
    factory = DummyClientFactory(
        get_responses=[
            DummyResponse(TEST_JWKS),
            DummyResponse({"name": "Di"}),
        ],
    )
    login = _login(GiteaOIDC10Login, factory)
    auth = await login.auth_url()
    id_token = _make_id_token(sub="gitea-999", email="di@example.com")
    factory.post_responses = [DummyResponse(_token_payload(id_token=id_token))]

    identity = await login.exchange("auth-code-123", auth["state"])

    assert identity["issuer"] == "gitea-oidc"
    assert identity["sub"] == "gitea-999"
    assert identity["email"] == "di@example.com"
    assert identity["name"] == "Di"
    _assert_token_post(factory)
    gets = factory.gets()
    assert [g["url"] for g in gets] == [
        METADATA["jwks_uri"],
        METADATA["userinfo_endpoint"],
    ]
    assert gets[1]["headers"]["Authorization"] == "Bearer access-123"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc10_exchange_uses_userinfo_when_email_missing() -> None:
    # Claims carry a name but no email, so the UserInfo lookup supplies
    # the email.
    factory = DummyClientFactory(
        get_responses=[
            DummyResponse(TEST_JWKS),
            DummyResponse({"email": "eve@example.com"}),
        ],
    )
    login = _login(GiteaOIDC10Login, factory)
    auth = await login.auth_url()
    id_token = _make_id_token(sub="gitea-111", name="Eve")
    factory.post_responses = [DummyResponse(_token_payload(id_token=id_token))]

    identity = await login.exchange("auth-code-123", auth["state"])

    assert identity["sub"] == "gitea-111"
    assert identity["email"] == "eve@example.com"
    assert identity["name"] == "Eve"
    assert [g["url"] for g in factory.gets()] == [
        METADATA["jwks_uri"],
        METADATA["userinfo_endpoint"],
    ]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc10_auth_url_discovers_endpoints_without_cache() -> None:
    factory = DummyClientFactory(
        get_responses=[DummyResponse(dict(METADATA))],
    )
    login = _login(GiteaOIDC10Login, factory, discovery_cache=False)

    auth = await login.auth_url()

    gets = factory.gets()
    assert len(gets) == 1
    assert gets[0]["url"] == DISCOVERY_ENDPOINT
    assert gets[0]["headers"] == {"Accept": "application/json"}
    assert auth["url"].startswith(f"{METADATA['authorization_endpoint']}?")
    parsed = parse_qs(urlsplit(auth["url"]).query)
    assert parsed["response_type"] == ["code"]
    assert parsed["scope"] == ["openid email profile"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc10_exchange_missing_id_token() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[DummyResponse(TEST_JWKS)],
    )
    login = _login(GiteaOIDC10Login, factory)
    auth = await login.auth_url()

    with pytest.raises(ValueError, match="no id_token"):
        await login.exchange("auth-code-123", auth["state"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_client_access_token_posts_client_credentials() -> None:
    factory = DummyClientFactory(
        post_responses=[
            DummyResponse({"access_token": "app-token-1", "expires_in": 3600})
        ],
    )
    client = _login(GiteaOAuth20AppClient, factory)

    token_a = await client.access_token()
    token_b = await client.access_token()

    assert token_a == "app-token-1"
    assert token_b == "app-token-1"
    posts = factory.posts()
    assert len(posts) == 1  # second call served from cache
    assert posts[0]["url"] == TOKEN_ENDPOINT
    assert posts[0]["data"] == {"grant_type": "client_credentials"}
    assert posts[0]["auth"] == (CLIENT_ID, "secret")
    assert posts[0]["headers"] == {"Accept": "application/json"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_client_access_token_passes_scope() -> None:
    factory = DummyClientFactory(
        post_responses=[
            DummyResponse({"access_token": "scoped-token", "expires_in": 3600})
        ],
    )
    client = _login(GiteaOAuth20AppClient, factory)

    token = await client.access_token("read:user")

    assert token == "scoped-token"
    assert factory.posts()[0]["data"] == {
        "grant_type": "client_credentials",
        "scope": "read:user",
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_client_access_token_posts_client_assertion() -> None:
    factory = DummyClientFactory(
        post_responses=[
            DummyResponse({"access_token": "app-token-2", "expires_in": 3600})
        ],
    )
    client = GiteaOAuth21AppClient(
        base_url=BASE_URL,
        client_id=CLIENT_ID,
        private_key_jwk=dict(TEST_PRIVATE_JWK),
    )
    client._http_client_factory = factory

    token = await client.access_token()

    assert token == "app-token-2"
    posts = factory.posts()
    assert len(posts) == 1
    assert posts[0]["url"] == TOKEN_ENDPOINT
    assert posts[0]["auth"] is None
    data = posts[0]["data"]
    assert data["grant_type"] == "client_credentials"
    assert data["client_id"] == CLIENT_ID
    assert data["client_assertion_type"] == (
        "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
    )
    signer = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(TEST_JWK))
    assertion = jwt.decode(
        data["client_assertion"],
        signer,
        algorithms=["RS256"],
        audience=TOKEN_ENDPOINT,
        issuer=CLIENT_ID,
    )
    assert assertion["iss"] == CLIENT_ID
    assert assertion["sub"] == CLIENT_ID


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_client_access_token_uses_secret_when_no_key() -> None:
    factory = DummyClientFactory(
        post_responses=[
            DummyResponse({"access_token": "app-token-3", "expires_in": 3600})
        ],
    )
    client = _login(GiteaOAuth21AppClient, factory)

    token = await client.access_token()

    assert token == "app-token-3"
    posts = factory.posts()
    assert len(posts) == 1
    assert posts[0]["url"] == TOKEN_ENDPOINT
    assert posts[0]["data"] == {"grant_type": "client_credentials"}
    assert posts[0]["auth"] == (CLIENT_ID, "secret")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc10_client_access_token_discovers_token_endpoint() -> None:
    factory = DummyClientFactory(
        post_responses=[
            DummyResponse({"access_token": "app-token-4", "expires_in": 3600})
        ],
        get_responses=[DummyResponse(dict(METADATA))],
    )
    client = _login(GiteaOIDC10AppClient, factory, discovery_cache=False)

    token = await client.access_token()

    assert token == "app-token-4"
    gets = factory.gets()
    assert len(gets) == 1
    assert gets[0]["url"] == DISCOVERY_ENDPOINT
    posts = factory.posts()
    assert len(posts) == 1
    assert posts[0]["url"] == TOKEN_ENDPOINT
    assert posts[0]["data"] == {"grant_type": "client_credentials"}
    assert posts[0]["auth"] == (CLIENT_ID, "secret")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_client_access_token_propagates_http_error() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"error": "server_error"}, status=500)],
    )
    client = _login(GiteaOAuth20AppClient, factory)

    with pytest.raises(FakeHTTPError):
        await client.access_token()
