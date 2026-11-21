"""Offline contract tests for the GitLab login and app-client flows (#6286).

Covers the primary public operation of each exported class, which the
existing unit tests only touch through resource/type checks, ``auth_url``
prefix checks, invalid-state failures, and token-cache behavior:

- ``GitLabOAuth20Login.auth_url``: self-hosted authorization endpoint and
  default ``read_user`` scope.
- ``GitLabOAuth20Login.exchange_and_identity``: token exchange + ``/user``
  mapping, including the ``public_email`` fallback, the ``username``
  fallback, and a custom ``api_base``.
- ``GitLabOAuth21Login.auth_url`` / ``GitLabOIDC10Login.exchange``: token
  exchange + ID token verification against a fake JWKS endpoint, with the
  ``preferred_username`` fallback and the UserInfo fallback only when the
  claims are incomplete.- ``auth_url`` without a preset discovery cache: issuer discovery through
  the fake client.
- ``GitLabOAuth20AppClient.access_token``: client-credentials POST (form,
  basic auth, scope) and cache reuse.
- ``GitLabOAuth21AppClient.access_token``: secret-auth and private-key
  client-assertion paths.
- ``GitLabOIDC10AppClient.access_token``: discovery-driven token endpoint.

Everything runs offline: a fake HTTP client serves discovery metadata,
token responses, UserInfo, and JWKS, and the ID tokens and client
assertions are signed with a throwaway RSA key generated for these tests.
No network access, credentials, or live GitLab account are needed, and
nothing here proves interoperability with GitLab's production service.
"""

from __future__ import annotations

import json
import time
from typing import Any
from urllib.parse import parse_qs, urlsplit

import jwt
import pytest
from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_gitlab import (
    GitLabOAuth20AppClient,
    GitLabOAuth20Login,
    GitLabOAuth21AppClient,
    GitLabOAuth21Login,
    GitLabOIDC10AppClient,
    GitLabOIDC10Login,
)
from swarmauri_base.auth_idp import verify_state

BASE_URL = "https://gitlab.example"
ISSUER = "https://gitlab.example"
CLIENT_ID = "client"
STATE_SECRET = b"0123456789abcdef0123456789abcdef"

METADATA = {
    "issuer": ISSUER,
    "authorization_endpoint": f"{BASE_URL}/oauth/authorize",
    "token_endpoint": f"{BASE_URL}/oauth/token",
    "userinfo_endpoint": f"{BASE_URL}/oauth/userinfo",
    "jwks_uri": f"{BASE_URL}/oauth/discovery/keys",
}

API_USER_ENDPOINT = f"{BASE_URL}/api/v4/user"
TOKEN_ENDPOINT = f"{BASE_URL}/oauth/token"
DISCOVERY_ENDPOINT = f"{ISSUER}/.well-known/openid-configuration"

# Throwaway RSA key for these tests only. The private half signs the ID
# tokens and the OAuth 2.1 client assertions below; the public half is
# served through the fake JWKS endpoint. It is never used outside this
# file.
TEST_PRIVATE_KEY_PEM = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCuEcVV9M+2rdrk\nP675tP0yuI7YXJbapvVhIPw96aTVvIwTFcqb0yOwkpx7vgpas1nJ6lmr+e7PBKuM\nnsi4E/kY7APIQIJgKTBd3DLp72o94YvkvzkyvzCUjj64tI6cWYFwOwHEZ47KkTIU\nJKJZKiGTh6kJzm+YskHs1r+EvNprZlg6YeNdAX+XbohI8qF/DggHdRB5siiPm495\nnEfBvS1hxVrjj2gSytIb8RpYMBzymE9rLw/862uJjFlu8glqtd+Tc7k4uNwjan5n\nSVwHt9xkNXj79G5gfvYpPr8fhL90gsbiZXuZR/ZXClZYjb2NzIDC7YrtV7xaeE0+\nzUG0no6FAgMBAAECggEAAbT/DLoBnOOl0ElZl21xcn+4sV5wB53NrWoYFgTGYUJN\nivmDbGZMyXdVdcHc77P1dqvBsQgs+XmOaoxl49erD9wZnCg+XYq20NRwrAvQpoBG\nI+gDHUZntW/ohwfkKgoFC+mvdnEQrxqsIAbfd6gMO7jVHc09n9P7sG1lpvvA8aNh\n3Ll27w4PDNDvqVvQDAFZHQ402VRpYk3Aeryhc9ynYw03sA+5N3X42bvcW1JeocVw\npgGnSDjYjPOc2Mwp5YMhr6w9jF4EWtv5M/eICWUkY0zyJnHZn4rPVYxZgKvUNTWc\n0g6HKKatrLFWkixV4d0TFGYBBRFu6Tu8G8K7VVsWbwKBgQDwMqqqImVbzBs2BgU7\ns+IT6E5gXNtrPRpqmuGKt47C8cyATPV1mtCFj/7yzdc5mp5f4goaTPkavg+KvGFE\noNTs6c+tGwDSbNx3i1DllS9qgG+H7uLkYXIc2OTGgnfUXV2h0iaEowWFG2C2nEEA\nySBdzkpaBWZMf9N82bqJRi2sCwKBgQC5hWPYFi9fxef41W+fDeeTEq9hTkAsN7I3\nBtwL5Gb+H/PRP9IaxyGjPiGiB1c6VMVBhGo4REgCGhd+sFeR0+Rb45akz+L6Y5AU\nN6mrLc640vBkcqHFrwXcbJjnwJGK4Sh9ey5KmvmeQdm8OvKW4s+D6UVVJNbXwCxF\nEWwKZ3a5rwKBgBAatYqWp8kR1Dk5ChzIoL3I84hOcX+tJxpCrCCK0g2L/LQVdNef\nu59Y2jUZS/bWwQuYsii1RHZgi9Y3byYUynHf80ad6t4w4k85jgD2kalIVzH7+EZr\nqiT4/c25baNVZzO0TVTTQUl9Xmyf6VPOKFdhv2ZtukAiyeEzD+ioReOlAoGAeqwI\nPE9XHgYYAILpXwvrr2VwkHAUoOhnMFmZ0UdDDxCDwT5pKIm55V5lEOW3uPtqv4rW\nTcRgtPsZxAzIqsWov1X7O5m25YhGMggoaedNRQs+J71g2P2Fa55ncP71fhaqFmcI\nUg6ttgam+f8kf78UJo5t6QIGCf2piDYf8bU+XUMCgYEAhehaV7xIYE2QmT/xYLt9\nuPktZy4NUK8yDPRUusCOhZ2ppMB0L5GsdgDwKXubg9YJXRzlP0x73QakpE9uJwxv\nlRunmoBa/5inh2em2jtOh/aBgO6s97P8KBBQPzMVTTjkvnezMHx497vU63K1K6Gq\nxexIDVXSEEE01rtJVdRf4ho=\n-----END PRIVATE KEY-----\n"
TEST_JWK = {
    "kty": "RSA",
    "kid": "test-key-1",
    "use": "sig",
    "alg": "RS256",
    "n": "rhHFVfTPtq3a5D-u-bT9MriO2FyW2qb1YSD8Pemk1byMExXKm9MjsJKce74KWrNZyepZq_nuzwSrjJ7IuBP5GOwDyECCYCkwXdwy6e9qPeGL5L85Mr8wlI4-uLSOnFmBcDsBxGeOypEyFCSiWSohk4epCc5vmLJB7Na_hLzaa2ZYOmHjXQF_l26ISPKhfw4IB3UQebIoj5uPeZxHwb0tYcVa449oEsrSG_EaWDAc8phPay8P_OtriYxZbvIJarXfk3O5OLjcI2p-Z0lcB7fcZDV4-_RuYH72KT6_H4S_dILG4mV7mUf2VwpWWI29jcyAwu2K7Ve8WnhNPs1BtJ6OhQ",
    "e": "AQAB",
}
TEST_PRIVATE_JWK = {
    "kty": "RSA",
    "kid": "test-key-2",
    "use": "sig",
    "alg": "RS256",
    "n": "rhHFVfTPtq3a5D-u-bT9MriO2FyW2qb1YSD8Pemk1byMExXKm9MjsJKce74KWrNZyepZq_nuzwSrjJ7IuBP5GOwDyECCYCkwXdwy6e9qPeGL5L85Mr8wlI4-uLSOnFmBcDsBxGeOypEyFCSiWSohk4epCc5vmLJB7Na_hLzaa2ZYOmHjXQF_l26ISPKhfw4IB3UQebIoj5uPeZxHwb0tYcVa449oEsrSG_EaWDAc8phPay8P_OtriYxZbvIJarXfk3O5OLjcI2p-Z0lcB7fcZDV4-_RuYH72KT6_H4S_dILG4mV7mUf2VwpWWI29jcyAwu2K7Ve8WnhNPs1BtJ6OhQ",
    "e": "AQAB",
    "d": "AbT_DLoBnOOl0ElZl21xcn-4sV5wB53NrWoYFgTGYUJNivmDbGZMyXdVdcHc77P1dqvBsQgs-XmOaoxl49erD9wZnCg-XYq20NRwrAvQpoBGI-gDHUZntW_ohwfkKgoFC-mvdnEQrxqsIAbfd6gMO7jVHc09n9P7sG1lpvvA8aNh3Ll27w4PDNDvqVvQDAFZHQ402VRpYk3Aeryhc9ynYw03sA-5N3X42bvcW1JeocVwpgGnSDjYjPOc2Mwp5YMhr6w9jF4EWtv5M_eICWUkY0zyJnHZn4rPVYxZgKvUNTWc0g6HKKatrLFWkixV4d0TFGYBBRFu6Tu8G8K7VVsWbw",
    "p": "8DKqqiJlW8wbNgYFO7PiE-hOYFzbaz0aaprhireOwvHMgEz1dZrQhY_-8s3XOZqeX-IKGkz5Gr4PirxhRKDU7OnPrRsA0mzcd4tQ5ZUvaoBvh-7i5GFyHNjkxoJ31F1dodImhKMFhRtgtpxBAMkgXc5KWgVmTH_TfNm6iUYtrAs",
    "q": "uYVj2BYvX8Xn-NVvnw3nkxKvYU5ALDeyNwbcC-Rm_h_z0T_SGschoz4hogdXOlTFQYRqOERIAhoXfrBXkdPkW-OWpM_i-mOQFDepqy3OuNLwZHKhxa8F3GyY58CRiuEofXsuSpr5nkHZvDryluLPg-lFVSTW18AsRRFsCmd2ua8",
    "dp": "EBq1ipanyRHUOTkKHMigvcjziE5xf60nGkKsIIrSDYv8tBV015-7n1jaNRlL9tbBC5iyKLVEdmCL1jdvJhTKcd_zRp3q3jDiTzmOAPaRqUhXMfv4RmuqJPj9zblto1VnM7RNVNNBSX1ebJ_pU84oV2G_Zm26QCLJ4TMP6KhF46U",
    "dq": "eqwIPE9XHgYYAILpXwvrr2VwkHAUoOhnMFmZ0UdDDxCDwT5pKIm55V5lEOW3uPtqv4rWTcRgtPsZxAzIqsWov1X7O5m25YhGMggoaedNRQs-J71g2P2Fa55ncP71fhaqFmcIUg6ttgam-f8kf78UJo5t6QIGCf2piDYf8bU-XUM",
    "qi": "hehaV7xIYE2QmT_xYLt9uPktZy4NUK8yDPRUusCOhZ2ppMB0L5GsdgDwKXubg9YJXRzlP0x73QakpE9uJwxvlRunmoBa_5inh2em2jtOh_aBgO6s97P8KBBQPzMVTTjkvnezMHx497vU63K1K6GqxexIDVXSEEE01rtJVdRf4ho",
}


class FakeHTTPError(Exception):
    """Raised by the fake client when a canned response carries an error status."""


class DummyResponse:
    def __init__(self, payload: dict[str, Any], status: int = 200):
        self._payload = payload
        self.status = status

    def raise_for_status(self) -> None:
        if self.status >= 400:
            raise FakeHTTPError(f"HTTP {self.status}")

    def json(self) -> dict[str, Any]:
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
    kwargs: dict[str, Any] = {
        "client_id": CLIENT_ID,
        "client_secret": SecretStr("secret"),
        "http_client_factory": factory,
    }
    if cls in (GitLabOAuth21Login, GitLabOIDC10Login, GitLabOIDC10AppClient):
        kwargs["issuer"] = ISSUER
    else:
        kwargs["base_url"] = BASE_URL
    if cls in (GitLabOAuth20Login, GitLabOAuth21Login, GitLabOIDC10Login):
        kwargs["redirect_uri"] = "https://example.com/callback"
        kwargs["state_secret"] = SecretBytes(STATE_SECRET)
    if api_base is not None:
        kwargs["api_base"] = api_base
    instance = cls(**kwargs)
    if discovery_cache and hasattr(instance, "discovery_cache"):
        instance.discovery_cache = dict(METADATA)
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
    login = _login(GitLabOAuth20Login, DummyClientFactory())

    auth = await login.auth_url()

    assert auth["url"].startswith(f"{BASE_URL}/oauth/authorize?")
    parsed = parse_qs(urlsplit(auth["url"]).query)
    assert parsed["response_type"] == ["code"]
    assert parsed["client_id"] == [CLIENT_ID]
    assert parsed["redirect_uri"] == ["https://example.com/callback"]
    assert parsed["scope"] == ["read_user"]
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
            DummyResponse({"id": 42, "email": "ada@example.com", "name": "Ada"})
        ],
    )
    login = _login(GitLabOAuth20Login, factory)
    auth = await login.auth_url()

    identity = await login.exchange_and_identity("auth-code-123", auth["state"])

    assert identity["issuer"] == "gitlab-oauth20"
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
async def test_oauth20_exchange_falls_back_to_public_email_and_username() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[
            DummyResponse(
                {
                    "id": 7,
                    "public_email": "bo@example.com",
                    "username": "bo",
                }
            )
        ],
    )
    login = _login(GitLabOAuth20Login, factory)
    auth = await login.auth_url()

    identity = await login.exchange_and_identity("auth-code-123", auth["state"])

    assert identity["sub"] == "7"
    assert identity["email"] == "bo@example.com"
    assert identity["name"] == "bo"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_uses_custom_api_base() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[
            DummyResponse({"id": 9, "email": "cy@example.com", "name": "Cy"})
        ],
    )
    login = _login(GitLabOAuth20Login, factory, api_base="https://api.gitlab.example")
    auth = await login.auth_url()

    identity = await login.exchange_and_identity("auth-code-123", auth["state"])

    assert identity["sub"] == "9"
    gets = factory.gets()
    assert len(gets) == 1
    assert gets[0]["url"] == "https://api.gitlab.example/user"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_auth_url_uses_discovery() -> None:
    login = _login(GitLabOAuth21Login, DummyClientFactory())

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
async def test_oauth21_exchange_returns_identity_from_id_token() -> None:
    factory = DummyClientFactory(
        get_responses=[DummyResponse({"keys": [TEST_JWK]})],
    )
    login = _login(GitLabOAuth21Login, factory)
    auth = await login.auth_url()
    id_token = _make_id_token(sub="gitlab-456", email="cy@example.com", name="Cy")
    factory.post_responses = [DummyResponse(_token_payload(id_token=id_token))]

    identity = await login.exchange_and_identity("auth-code-123", auth["state"])

    assert identity["issuer"] == "gitlab-oauth21"
    assert identity["sub"] == "gitlab-456"
    assert identity["email"] == "cy@example.com"
    assert identity["name"] == "Cy"
    assert identity["raw"]["claims"]["sub"] == "gitlab-456"
    _assert_token_post(factory)
    gets = factory.gets()
    assert len(gets) == 1
    assert gets[0]["url"] == METADATA["jwks_uri"]
    assert gets[0]["headers"] == {"Accept": "application/json"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_exchange_falls_back_to_preferred_username() -> None:
    # Claims carry email + preferred_username but no name; unlike the
    # Google mixin, this mixin counts preferred_username as the name,
    # so no UserInfo lookup happens and the identity falls back to it.
    factory = DummyClientFactory(
        get_responses=[DummyResponse({"keys": [TEST_JWK]})],
    )
    login = _login(GitLabOAuth21Login, factory)
    auth = await login.auth_url()
    id_token = _make_id_token(
        sub="gitlab-789",
        email="bo@example.com",
        preferred_username="bo",
    )
    factory.post_responses = [DummyResponse(_token_payload(id_token=id_token))]

    identity = await login.exchange_and_identity("auth-code-123", auth["state"])

    assert identity["sub"] == "gitlab-789"
    assert identity["email"] == "bo@example.com"
    assert identity["name"] == "bo"
    assert [g["url"] for g in factory.gets()] == [METADATA["jwks_uri"]]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc10_exchange_uses_userinfo_when_claims_incomplete() -> None:
    factory = DummyClientFactory(
        get_responses=[
            DummyResponse({"keys": [TEST_JWK]}),
            DummyResponse(
                {
                    "sub": "gitlab-999",
                    "email": "di@example.com",
                    "name": "Di",
                }
            ),
        ],
    )
    login = _login(GitLabOIDC10Login, factory)
    auth = await login.auth_url()
    id_token = _make_id_token(sub="gitlab-999")
    factory.post_responses = [DummyResponse(_token_payload(id_token=id_token))]

    identity = await login.exchange("auth-code-123", auth["state"])

    assert identity["issuer"] == "gitlab-oidc"
    assert identity["sub"] == "gitlab-999"
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
async def test_oidc10_exchange_skips_userinfo_when_claims_complete() -> None:
    factory = DummyClientFactory(
        get_responses=[DummyResponse({"keys": [TEST_JWK]})],
    )
    login = _login(GitLabOIDC10Login, factory)
    auth = await login.auth_url()
    id_token = _make_id_token(sub="gitlab-111", email="eve@example.com", name="Eve")
    factory.post_responses = [DummyResponse(_token_payload(id_token=id_token))]

    identity = await login.exchange("auth-code-123", auth["state"])

    assert identity["sub"] == "gitlab-111"
    assert identity["email"] == "eve@example.com"
    assert identity["name"] == "Eve"
    assert len(factory.gets()) == 1  # JWKS only, no UserInfo call


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc10_auth_url_discovers_endpoints_without_cache() -> None:
    factory = DummyClientFactory(
        get_responses=[DummyResponse(dict(METADATA))],
    )
    login = _login(GitLabOIDC10Login, factory, discovery_cache=False)

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
async def test_oauth20_exchange_propagates_provider_http_error() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"error": "server_error"}, status=500)],
    )
    login = _login(GitLabOAuth20Login, factory)
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
    login = _login(GitLabOAuth20Login, factory)
    auth = await login.auth_url()

    with pytest.raises(KeyError):
        await login.exchange_and_identity("auth-code-123", auth["state"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_exchange_missing_id_token() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[DummyResponse({"keys": [TEST_JWK]})],
    )
    login = _login(GitLabOAuth21Login, factory)
    auth = await login.auth_url()

    with pytest.raises(ValueError, match="no id_token"):
        await login.exchange_and_identity("auth-code-123", auth["state"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_client_access_token_posts_client_credentials() -> None:
    factory = DummyClientFactory(
        post_responses=[
            DummyResponse({"access_token": "app-token-1", "expires_in": 3600})
        ],
    )
    client = _login(GitLabOAuth20AppClient, factory)

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
    client = _login(GitLabOAuth20AppClient, factory)

    token = await client.access_token("api")

    assert token == "scoped-token"
    assert factory.posts()[0]["data"] == {
        "grant_type": "client_credentials",
        "scope": "api",
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_client_access_token_posts_client_assertion() -> None:
    factory = DummyClientFactory(
        post_responses=[
            DummyResponse({"access_token": "app-token-2", "expires_in": 3600})
        ],
    )
    client = GitLabOAuth21AppClient(
        base_url=BASE_URL,
        client_id=CLIENT_ID,
        private_key_jwk=dict(TEST_PRIVATE_JWK),
        http_client_factory=factory,
    )

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
    client = _login(GitLabOAuth21AppClient, factory)

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
    client = _login(GitLabOIDC10AppClient, factory, discovery_cache=False)

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
    client = _login(GitLabOAuth20AppClient, factory)

    with pytest.raises(FakeHTTPError):
        await client.access_token()
