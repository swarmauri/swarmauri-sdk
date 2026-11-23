"""Offline contract tests for the Okta login flows (#6292).

Covers the primary public operation of each login class, which the
existing unit tests only touch through ``auth_url`` prefix checks and
invalid-state failures:

- ``OktaOAuth20Login.exchange_and_identity``: token exchange + UserInfo
  mapping, including the ``sub`` fallback chain.
- ``OktaOAuth21Login.exchange_and_identity``: token exchange + ID token
  verification against a fake JWKS endpoint.
- ``OktaOIDC10Login.exchange``: token exchange + ID token verification,
  with the UserInfo fallback only when the claims are incomplete.
- ``auth_url`` without a preset discovery cache: issuer discovery through
  the fake client, and ``prompt=consent`` on the authorization URL.

Everything runs offline: a fake HTTP client serves discovery metadata,
token responses, UserInfo, and JWKS, and the ID tokens are signed with a
throwaway RSA key generated for these tests. No network access,
credentials, or live Okta account are needed, and nothing here proves
interoperability with Okta's production service.
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

from swarmauri_auth_idp_okta import (
    OktaOAuth20Login,
    OktaOAuth21Login,
    OktaOIDC10Login,
)
from swarmauri_base.auth_idp import verify_state

ISSUER = "https://example.okta.com/oauth2/default"
CLIENT_ID = "client"

METADATA = {
    "authorization_endpoint": f"{ISSUER}/v1/authorize",
    "token_endpoint": f"{ISSUER}/v1/token",
    "userinfo_endpoint": f"{ISSUER}/v1/userinfo",
    "jwks_uri": f"{ISSUER}/v1/keys",
}

# Throwaway RSA key for these tests only. The private half signs the ID
# tokens below; the public half is served through the fake JWKS endpoint.
# It is never used outside this file.
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
    """A canned response returned an HTTP error status."""


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


def _login(cls, factory, *, discovery_cache=True):
    instance = cls(
        issuer=ISSUER,
        client_id=CLIENT_ID,
        client_secret=SecretStr("secret"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"0123456789abcdef0123456789abcdef"),
        http_client_factory=factory,
    )
    if discovery_cache:
        instance.discovery_cache = dict(METADATA)
    return instance


def _token_payload(*, id_token: Optional[str] = None) -> Dict[str, Any]:
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


def _verifier_for(state: str) -> str:
    return verify_state(b"0123456789abcdef0123456789abcdef", state)["verifier"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_returns_identity_from_userinfo() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[
            DummyResponse(
                {"sub": "00u123", "email": "ada@example.com", "name": "Ada"}
            )
        ],
    )
    login = _login(OktaOAuth20Login, factory)
    auth = await login.auth_url()

    identity = await login.exchange_and_identity(
        "auth-code-123", auth["state"]
    )

    assert identity["issuer"] == "okta-oauth20"
    assert identity["sub"] == "00u123"
    assert identity["email"] == "ada@example.com"
    assert identity["name"] == "Ada"
    assert identity["raw"]["tokens"]["access_token"] == "access-123"
    assert identity["raw"]["userinfo"]["sub"] == "00u123"
    data = _assert_token_post(factory)
    assert data["code_verifier"] == _verifier_for(auth["state"])
    gets = factory.gets()
    assert len(gets) == 1
    assert gets[0]["url"] == METADATA["userinfo_endpoint"]
    assert gets[0]["headers"] == {
        "Authorization": "Bearer access-123",
        "Accept": "application/json",
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_falls_back_to_uid_and_given_name() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
        get_responses=[
            DummyResponse(
                {"uid": "uid-9", "email": "bo@example.com", "given_name": "Bo"}
            )
        ],
    )
    login = _login(OktaOAuth20Login, factory)
    auth = await login.auth_url()

    identity = await login.exchange_and_identity(
        "auth-code-123", auth["state"]
    )

    assert identity["sub"] == "uid-9"
    assert identity["email"] == "bo@example.com"
    assert identity["name"] == "Bo"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_exchange_returns_identity_from_id_token() -> None:
    id_token = _make_id_token(
        sub="00u456",
        email="cy@example.com",
        name="Cy",
        preferred_username="cy",
    )
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload(id_token=id_token))],
        get_responses=[DummyResponse(TEST_JWKS)],
    )
    login = _login(OktaOAuth21Login, factory)
    auth = await login.auth_url()

    identity = await login.exchange_and_identity(
        "auth-code-123", auth["state"]
    )

    assert identity["issuer"] == "okta-oauth21"
    assert identity["sub"] == "00u456"
    assert identity["email"] == "cy@example.com"
    assert identity["name"] == "Cy"
    assert identity["raw"]["claims"]["sub"] == "00u456"
    _assert_token_post(factory)
    gets = factory.gets()
    assert len(gets) == 1
    assert gets[0]["url"] == METADATA["jwks_uri"]
    assert gets[0]["headers"] == {"Accept": "application/json"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc10_exchange_uses_userinfo_when_claims_incomplete() -> None:
    id_token = _make_id_token(sub="00u789", preferred_username="di")
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload(id_token=id_token))],
        get_responses=[
            DummyResponse(TEST_JWKS),
            DummyResponse(
                {"sub": "00u789", "email": "di@example.com", "name": "Di"}
            ),
        ],
    )
    login = _login(OktaOIDC10Login, factory)
    auth = await login.auth_url()

    identity = await login.exchange("auth-code-123", auth["state"])

    assert identity["issuer"] == "okta-oidc"
    assert identity["sub"] == "00u789"
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
    id_token = _make_id_token(
        sub="00u999",
        email="eve@example.com",
        name="Eve",
    )
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload(id_token=id_token))],
        get_responses=[DummyResponse(TEST_JWKS)],
    )
    login = _login(OktaOIDC10Login, factory)
    auth = await login.auth_url()

    identity = await login.exchange("auth-code-123", auth["state"])

    assert identity["sub"] == "00u999"
    assert identity["email"] == "eve@example.com"
    assert identity["name"] == "Eve"
    assert len(factory.gets()) == 1  # JWKS only, no UserInfo call


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_discovers_endpoint_and_requests_consent() -> None:
    factory = DummyClientFactory(
        get_responses=[DummyResponse(dict(METADATA))],
    )
    login = _login(OktaOAuth20Login, factory, discovery_cache=False)

    auth = await login.auth_url()

    gets = factory.gets()
    assert len(gets) == 1
    assert gets[0]["url"] == f"{ISSUER}/.well-known/openid-configuration"
    assert auth["url"].startswith(f"{METADATA['authorization_endpoint']}?")
    parsed = parse_qs(urlsplit(auth["url"]).query)
    assert parsed["response_type"] == ["code"]
    assert parsed["prompt"] == ["consent"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_propagates_provider_http_error() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse({"error": "server_error"}, status=500)],
    )
    login = _login(OktaOAuth20Login, factory)
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
    login = _login(OktaOAuth20Login, factory)
    auth = await login.auth_url()

    with pytest.raises(KeyError):
        await login.exchange_and_identity("auth-code-123", auth["state"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_exchange_missing_id_token() -> None:
    factory = DummyClientFactory(
        post_responses=[DummyResponse(_token_payload())],
    )
    login = _login(OktaOAuth21Login, factory)
    auth = await login.auth_url()

    with pytest.raises(ValueError, match="no id_token"):
        await login.exchange_and_identity("auth-code-123", auth["state"])
