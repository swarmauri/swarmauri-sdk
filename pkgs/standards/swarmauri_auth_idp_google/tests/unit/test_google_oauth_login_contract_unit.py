"""Offline contract tests for the Google login flows (#6288).

Covers the primary public operation of each exported login class, which
the existing unit tests only touch through ``auth_url`` prefix checks and
invalid-state failures:

- ``GoogleOAuth20Login.auth_url``: offline access + account selection
  parameters on the authorization URL.
- ``GoogleOAuth20Login.exchange_and_identity``: token exchange + UserInfo
  mapping, including the Google profile ``id`` -> ``sub`` mapping.
- ``GoogleOAuth21Login.auth_url``: discovery-driven authorization URL with
  nonce, ``include_granted_scopes``, and account selection.
- ``GoogleOAuth21Login.exchange_and_identity``: token exchange + ID token
  verification against a fake JWKS endpoint, with the ``given_name``
  fallback (note: a missing ``name`` claim still triggers the UserInfo
  lookup, since the mixin fetches it whenever email or name is absent).
- ``GoogleOIDC10Login.exchange``: token exchange + ID token verification,
  with the UserInfo fallback only when the claims are incomplete.
- ``auth_url`` without a preset discovery cache: issuer discovery through
  the fake client.

Everything runs offline: a fake HTTP client serves discovery metadata,
token responses, UserInfo, and JWKS, and the ID tokens are signed with a
throwaway RSA key generated for these tests. No network access,
credentials, or live Google account are needed, and nothing here proves
interoperability with Google's production service.
"""

from __future__ import annotations

import time
from typing import Any
from urllib.parse import parse_qs, urlsplit

import jwt
import pytest
from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_google import (
    GoogleOAuth20Login,
    GoogleOAuth21Login,
    GoogleOIDC10Login,
)
from swarmauri_base.auth_idp import verify_state

ISSUER = "https://accounts.google.com"
CLIENT_ID = "client"
STATE_SECRET = b"0123456789abcdef0123456789abcdef"

METADATA = {
    "issuer": ISSUER,
    "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
    "token_endpoint": "https://oauth2.googleapis.com/token",
    "userinfo_endpoint": "https://www.googleapis.com/oauth2/v2/userinfo",
    "jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
}

OAUTH20_USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v1/userinfo?alt=json"

# Throwaway RSA key for these tests only. The private half signs the ID
# tokens below; the public half is served through the fake JWKS endpoint.
# It is never used outside this file.
TEST_PRIVATE_KEY_PEM = "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDIIR4JGyix80SL\nQ89ddpVlWVTVzlMt/ydC7bdsz6bdXdi51+yogFyDZwKlVxjdpz9x0JdAWXNHOC1s\n3MSL5L9mMYltUn+/ejvuEeFg4KvZImIUMow8xOHuj4o7ezUY7fJ1qlHt7EJw4Dl8\ncTKLybjTkGF/HFF3F2I/eK4X5Q2QTYcRFNlQPkqmMYhc46ZhmRumh5EyuTmhbKoS\nKOAHyd4tyVOniKK+LdmQxPmfSqiLbq7EmzkEWj7eKKkKFpNITkNr55TakQ1MPhWK\njDbTWmmmx4CEWGF65yfSeRsdhVh0WajAA/P+Chjn3eq9TL3Kp9Loi1MW78lMsJbZ\nNEKpndItAgMBAAECggEAAIaXFHFgp9MFR5O2hul/AU9SRJDbBsBoWH8qX7FN9WqV\nMqvJYInxyZtAK7IGYTKwHSWYosp5XeMHui+m890hJEIWDoD3JUggwdfZ2TjN4Bn8\nhaQPr+sufW4dcAQ7V/pBYaNrEq5vtZSJN3VOq4UB+iBOI+4tnUak80NnEFisMp2t\nqZxO+RJwzXo1a9R6vNrFICyRT4iJ1uBGeW6sL+sLCZf4nPkivm4mMxt7xPIewIeN\nCNSRRvAnIdsqRI490Smr2cI7RXEzZnFVbfK60idAZ1iPtDE8CzR3SWdY0O4+TX0z\nnETQk1f0kf+qkXO8mQCvaCE7mMkpraZ1rok4dOwe4QKBgQD38JtGVJJqDFABdds1\nPXBWJpw8n3YR/N/iA7QylV6PlECuHd826G0/4gAnIt+SbcoGlZgHApKyt1VM2+M2\ntmqf1E5k6gvKSMQ+UpghBo+1qYrR8kaLk4lVcpXo5oH/cyWtz84mrRT0cQ5fn01C\nfCvGVyRiDAgwdhdJLq5S4BetvQKBgQDOop/cw4tZ6Gx1P+ajM0PQPTcvv1nlWodN\n0cTLTGhmL/LnC6Vhk367/wnmar1RH2xOZp7qYMylqfoVeIiNx+6F9SclBl7WAaQp\nE4jfs2f8NUv5CR2gtkiFfuoOXRbTlCewY0+PIBc42pQ27fZ8cAP9emUeHlgpWT5a\nzppE01JlMQKBgQDftGS1CTttmZxaJPdaywtff8i53fqO8kUiTMs6VJEUJORS9Trf\n9MgVupj+trVYDd0ZIcIgmQ65VzcMeN1CEUaU3N66qH1oz0zZGnaOXbguZUGOefVy\nm/Rud0uQ7uHeFQurDnLnbIUapCMe3cG8ugJZG2kFWevNpc8OxaKdvfk/VQKBgQCk\nSbQkh+xhfWPODRJIq1e9Vw5rjg3hRorRGnkG0icnJ/ROMno5DFX1Dp9GbZM7zmoE\nI58x5eiPxocpTv3zDATeyL1ouJnqOL/WUMvAYBnK8m0HAXJm9sbOLMvWw7iEXAT6\nPttghjkwYMj6q1QQN9dUT13aBnI93dCvzhflpMab4QKBgQDqTe3Svoaw4tHrjpNJ\nhk3THG6g/n7UpxNSYAHembAhSzb7QCkgJk/EmHiG+HFnEUhaL/cX4mR2oSpFJ8IC\nim5tTdKRSVtWRYY467czK7zCJ7iycgbvsp/hfVyDdXeHwvW1OUNPNgzdL31mk3cT\npuq+4OZG3lkDndQ3QMZRKx2S+g==\n-----END PRIVATE KEY-----\n"
TEST_JWK = {
    "kty": "RSA",
    "kid": "test-key-1",
    "use": "sig",
    "alg": "RS256",
    "n": "yCEeCRsosfNEi0PPXXaVZVlU1c5TLf8nQu23bM-m3V3YudfsqIBcg2cCpVcY3ac_cdCXQFlzRzgtbNzEi-S_ZjGJbVJ_v3o77hHhYOCr2SJiFDKMPMTh7o-KO3s1GO3ydapR7exCcOA5fHEyi8m405BhfxxRdxdiP3iuF-UNkE2HERTZUD5KpjGIXOOmYZkbpoeRMrk5oWyqEijgB8neLclTp4iivi3ZkMT5n0qoi26uxJs5BFo-3iipChaTSE5Da-eU2pENTD4Viow201pppseAhFhheucn0nkbHYVYdFmowAPz_goY593qvUy9yqfS6ItTFu_JTLCW2TRCqZ3SLQ",
    "e": "AQAB",
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
    nonce: str | None = None,
    email: str | None = None,
    name: str | None = None,
    given_name: str | None = None,
) -> str:
    now = int(time.time())
    claims: dict[str, Any] = {
        "sub": sub,
        "iss": ISSUER,
        "aud": CLIENT_ID,
        "iat": now,
        "exp": now + 600,
    }
    if nonce is not None:
        claims["nonce"] = nonce
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
        client_id=CLIENT_ID,
        client_secret=SecretStr("secret"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(STATE_SECRET),
        http_client_factory=factory,
    )
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
    assert post["url"] == METADATA["token_endpoint"]
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
async def test_oauth20_auth_url_requests_offline_access() -> None:
    login = _login(GoogleOAuth20Login, DummyClientFactory())

    auth = await login.auth_url()

    assert auth["url"].startswith("https://accounts.google.com/o/oauth2/v2/auth?")
    parsed = parse_qs(urlsplit(auth["url"]).query)
    assert parsed["response_type"] == ["code"]
    assert parsed["client_id"] == [CLIENT_ID]
    assert parsed["redirect_uri"] == ["https://example.com/callback"]
    assert parsed["access_type"] == ["offline"]
    assert parsed["prompt"] == ["select_account"]
    assert parsed["code_challenge_method"] == ["S256"]
    assert parsed["code_challenge"]
    scope = parsed["scope"][0]
    assert "https://www.googleapis.com/auth/userinfo.email" in scope
    assert "https://www.googleapis.com/auth/userinfo.profile" in scope
    payload = _state_payload(auth["state"])
    assert payload["verifier"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_returns_identity_from_userinfo() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[
            DummyResponse(
                {
                    "id": "google-123",
                    "email": "ada@example.com",
                    "name": "Ada",
                }
            )
        ],
    )
    login = _login(GoogleOAuth20Login, factory)
    auth = await login.auth_url()

    identity = await login.exchange_and_identity("auth-code-123", auth["state"])

    assert identity["issuer"] == "google-oauth20"
    assert identity["sub"] == "google-123"
    assert identity["email"] == "ada@example.com"
    assert identity["name"] == "Ada"
    assert identity["raw"]["tokens"]["access_token"] == "access-123"
    assert identity["raw"]["userinfo"]["id"] == "google-123"
    data = _assert_token_post(factory)
    assert data["code_verifier"] == _state_payload(auth["state"])["verifier"]
    gets = factory.gets()
    assert len(gets) == 1
    assert gets[0]["url"] == OAUTH20_USERINFO_ENDPOINT
    assert gets[0]["headers"] == {
        "Authorization": "Bearer access-123",
        "Accept": "application/json",
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_auth_url_requests_nonce_and_account_selection() -> None:
    login = _login(GoogleOAuth21Login, DummyClientFactory())

    auth = await login.auth_url()

    assert auth["url"].startswith("https://accounts.google.com/o/oauth2/v2/auth?")
    parsed = parse_qs(urlsplit(auth["url"]).query)
    assert parsed["response_type"] == ["code"]
    assert parsed["scope"] == ["openid email profile"]
    assert parsed["prompt"] == ["select_account"]
    assert parsed["include_granted_scopes"] == ["true"]
    assert parsed["code_challenge_method"] == ["S256"]
    assert parsed["nonce"]
    assert parsed["nonce"] == [_state_payload(auth["state"])["nonce"]]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_exchange_returns_identity_from_id_token() -> None:
    factory = DummyClientFactory(
        get_responses=[DummyResponse({"keys": [TEST_JWK]})],
    )
    login = _login(GoogleOAuth21Login, factory)
    auth = await login.auth_url()
    nonce = _state_payload(auth["state"])["nonce"]
    id_token = _make_id_token(
        sub="google-456",
        nonce=nonce,
        email="cy@example.com",
        name="Cy",
    )
    factory.post_responses = [DummyResponse(_token_payload(id_token=id_token))]

    identity = await login.exchange_and_identity("auth-code-123", auth["state"])

    assert identity["issuer"] == "google-oauth21"
    assert identity["sub"] == "google-456"
    assert identity["email"] == "cy@example.com"
    assert identity["name"] == "Cy"
    assert identity["raw"]["claims"]["sub"] == "google-456"
    _assert_token_post(factory)
    gets = factory.gets()
    assert len(gets) == 1
    assert gets[0]["url"] == METADATA["jwks_uri"]
    assert gets[0]["headers"] == {"Accept": "application/json"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_exchange_falls_back_to_given_name() -> None:
    # Claims carry email + given_name but no name, so the mixin still
    # consults UserInfo (it fetches whenever email or name is absent);
    # the UserInfo reply below has no name, so the identity falls back
    # to the given_name claim.
    factory = DummyClientFactory(
        get_responses=[
            DummyResponse({"keys": [TEST_JWK]}),
            DummyResponse({"sub": "google-789", "email": "bo@example.com"}),
        ],
    )
    login = _login(GoogleOAuth21Login, factory)
    auth = await login.auth_url()
    nonce = _state_payload(auth["state"])["nonce"]
    id_token = _make_id_token(
        sub="google-789",
        nonce=nonce,
        email="bo@example.com",
        given_name="Bo",
    )
    factory.post_responses = [DummyResponse(_token_payload(id_token=id_token))]

    identity = await login.exchange_and_identity("auth-code-123", auth["state"])

    assert identity["sub"] == "google-789"
    assert identity["email"] == "bo@example.com"
    assert identity["name"] == "Bo"
    assert [g["url"] for g in factory.gets()] == [
        METADATA["jwks_uri"],
        METADATA["userinfo_endpoint"],
    ]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc10_exchange_uses_userinfo_when_claims_incomplete() -> None:
    factory = DummyClientFactory(
        get_responses=[
            DummyResponse({"keys": [TEST_JWK]}),
            DummyResponse(
                {
                    "sub": "google-999",
                    "email": "di@example.com",
                    "name": "Di",
                }
            ),
        ],
    )
    login = _login(GoogleOIDC10Login, factory)
    auth = await login.auth_url()
    nonce = _state_payload(auth["state"])["nonce"]
    id_token = _make_id_token(sub="google-999", nonce=nonce)
    factory.post_responses = [DummyResponse(_token_payload(id_token=id_token))]

    identity = await login.exchange("auth-code-123", auth["state"])

    assert identity["issuer"] == "google-oidc"
    assert identity["sub"] == "google-999"
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
    login = _login(GoogleOIDC10Login, factory)
    auth = await login.auth_url()
    nonce = _state_payload(auth["state"])["nonce"]
    id_token = _make_id_token(
        sub="google-111",
        nonce=nonce,
        email="eve@example.com",
        name="Eve",
    )
    factory.post_responses = [DummyResponse(_token_payload(id_token=id_token))]

    identity = await login.exchange("auth-code-123", auth["state"])

    assert identity["sub"] == "google-111"
    assert identity["email"] == "eve@example.com"
    assert identity["name"] == "Eve"
    assert len(factory.gets()) == 1  # JWKS only, no UserInfo call


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc10_auth_url_discovers_endpoints_without_cache() -> None:
    factory = DummyClientFactory(
        get_responses=[DummyResponse(dict(METADATA))],
    )
    login = _login(GoogleOIDC10Login, factory, discovery_cache=False)

    auth = await login.auth_url()

    gets = factory.gets()
    assert len(gets) == 1
    assert gets[0]["url"] == (
        "https://accounts.google.com/.well-known/openid-configuration"
    )
    assert gets[0]["headers"] == {"Accept": "application/json"}
    assert auth["url"].startswith(f"{METADATA['authorization_endpoint']}?")
    parsed = parse_qs(urlsplit(auth["url"]).query)
    assert parsed["response_type"] == ["code"]
    assert parsed["prompt"] == ["select_account"]
    assert parsed["include_granted_scopes"] == ["true"]
    assert parsed["nonce"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_propagates_provider_http_error() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"error": "server_error"}, status=500)],
    )
    login = _login(GoogleOAuth20Login, factory)
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
    login = _login(GoogleOAuth20Login, factory)
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
    login = _login(GoogleOAuth21Login, factory)
    auth = await login.auth_url()

    with pytest.raises(ValueError, match="no id_token"):
        await login.exchange_and_identity("auth-code-123", auth["state"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc10_exchange_rejects_nonce_mismatch() -> None:
    factory = DummyClientFactory(
        get_responses=[DummyResponse({"keys": [TEST_JWK]})],
    )
    login = _login(GoogleOIDC10Login, factory)
    auth = await login.auth_url()
    id_token = _make_id_token(
        sub="google-222",
        nonce="wrong-nonce",
        email="mallory@example.com",
        name="Mallory",
    )
    factory.post_responses = [DummyResponse(_token_payload(id_token=id_token))]

    with pytest.raises(ValueError, match="nonce mismatch"):
        await login.exchange("auth-code-123", auth["state"])
