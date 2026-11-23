"""Offline contract tests for the Apple Sign-in logins and app clients
(#6272).

Covers the primary public operation of each exported class, which the
existing unit tests only touch through resource/type checks, ``auth_url``
prefix checks, invalid-state failures, and the app-client unsupported
grant:

- ``AppleOAuth20Login.auth_url``: fixed Apple authorization endpoint,
  default ``name email`` scope, nonce propagation, and PKCE S256.
- ``AppleOAuth20Login.exchange_and_identity``: token POST (URL, form
  fields, ES256 client-secret JWT contents), JWKS fetch, ID-token
  verification, and identity mapping.
- ``AppleOAuth21Login.auth_url`` / ``exchange_and_identity``: same
  contract driven by OIDC discovery, including discovery caching.
- ``AppleOIDC10Login.auth_url`` / ``exchange``: discovery-driven flow
  with the same identity mapping.
- ``AppleOAuth20AppClient`` / ``AppleOAuth21AppClient`` /
  ``AppleOIDC10AppClient``: ``access_token`` raises the documented
  unsupported-grant error (Apple issues no generic client-credentials
  tokens).
- Client-secret JWT fields: ``iss``/``sub``/``aud``/``kid``/``exp`` and
  the ES256 signature, checked against a throwaway local key.

Everything runs offline: a fake HTTP client serves discovery metadata,
token responses, and JWKS, and the ID tokens are signed with a throwaway
RSA key generated for these tests. No network access, credentials, or
live Apple account are needed, and nothing here proves interoperability
with Apple's production service.
"""

from __future__ import annotations

import base64
import hashlib
import time
from typing import Any
from urllib.parse import parse_qs, urlsplit

import httpx
import jwt
import pytest
from pydantic import SecretBytes

from swarmauri_auth_idp_apple import (
    AppleOAuth20AppClient,
    AppleOAuth20Login,
    AppleOAuth21AppClient,
    AppleOAuth21Login,
    AppleOIDC10AppClient,
    AppleOIDC10Login,
)
from swarmauri_auth_idp_apple.internal import APPLE_ISSUER
from swarmauri_base.auth_idp import verify_state

TEAM_ID = "team-id-123"
KEY_ID = "key-id-456"
CLIENT_ID = "com.example.app"
REDIRECT_URI = "https://example.com/callback"
STATE_SECRET = b"test-state-secret-32-bytes-long!!"

AUTH_ENDPOINT = "https://appleid.apple.com/auth/authorize"
TOKEN_ENDPOINT = "https://appleid.apple.com/auth/token"
JWKS_URI = "https://appleid.apple.com/auth/keys"
DISCOVERY_URL = "https://appleid.apple.com/.well-known/openid-configuration"

METADATA = {
    "issuer": APPLE_ISSUER,
    "authorization_endpoint": "https://apple.example/authorize",
    "token_endpoint": "https://apple.example/token",
    "userinfo_endpoint": "https://apple.example/userinfo",
    "jwks_uri": "https://apple.example/keys",
}

# Throwaway EC key for these tests only. The private half signs the Apple
# client-secret JWTs; the public half verifies them. It is never used
# outside this file.
TEST_EC_PRIVATE_KEY_PEM = (
    "-----BEGIN PRIVATE KEY-----\n"
    "MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgFJn3Ljf0NP3Ou11A\n"
    "9g34efhujjHMsU4370Lvyl1+ohShRANCAAS5HiDTLsultFTl29JVoLnykboeS3Im\n"
    "+lptJy2j7b76oNpVWCytjhH4hOTy021z1r4wzu4wTPYRHCNG5lV9i3/i\n"
    "-----END PRIVATE KEY-----\n"
)
TEST_EC_PUBLIC_KEY_PEM = (
    "-----BEGIN PUBLIC KEY-----\n"
    "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEuR4g0y7LpbRU5dvSVaC58pG6Hkty\n"
    "JvpabScto+2++qDaVVgsrY4R+ITk8tNtc9a+MM7uMEz2ERwjRuZVfYt/4g==\n"
    "-----END PUBLIC KEY-----\n"
)

# Throwaway RSA key for these tests only. The private half signs the ID
# tokens; the public half is served through the fake JWKS endpoint.
TEST_RSA_PRIVATE_KEY_PEM = (
    "-----BEGIN PRIVATE KEY-----\n"
    "MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDFX1qnMuCoVL+W\n"
    "qG6JYgb1o450IwwqGXIFwbeNPD5cRu1iyPPYLR9XbepBSc31jMWo25b+u+LLKbIL\n"
    "1kfDJfoR6wg0reYc2snOP86W9MEjcCuWC9zT0wda+zlVrKWp3CreyROetCrS9n2b\n"
    "I3wxOPrwy37OT4QTlV34ualI3MHUufckz8aCTC4v4iwbCwFmeY6FNvF8KuVcyIkF\n"
    "sId6c0O0iSoeJuoqM22b9KlCxLjnewLCYpKZE3EKrhtIXXSo2oul5mqFRNAOZ27w\n"
    "SQrwKzIJY3uL7KzJ6m7FsEDpoAncSyj6tjnS+liUNGWZlf0U1K2uTDCOxeUD+Wjj\n"
    "1NFXacBdAgMBAAECggEADG9ahcg10UUtoO9Rr4QmjhlU40pF/O0Hewdeah6Oiz/I\n"
    "uv2QJ2GIZPi+1ogw2rSYy2+yTrBFtKkW15oTgV8GJ1TYeoEuS0kZh84LVQVsma/6\n"
    "fwSWUB4ui3Pig9xRv6boaIrgmpIdVJdFCJ4ut+cwIDWh8pud5aH2frIr0TRfXeiR\n"
    "JqNj+SUlXu6PY1cXmzahXGOeMezMphq99Cj5eB2oJajRJugzyE8lq/j4ATszgbfl\n"
    "IWJYy1ZIu2mtI3uEwMZ56bJpsbwLfZgri/o6vNDpcJEMKKbEFNL4sqtnrlknhW9t\n"
    "e0rkDz8AeHe2W8PbEHi+V4Cgjvx+PIZo5rQAV3FGHQKBgQDsO0nDoC4rnBiVKmhQ\n"
    "efwwtS6WU3gnbPwlavgOxSY1FVLxBddJYEzITiQpe8AboIbfMah6MB1bIVzTD859\n"
    "4Umv+e7wPmUU2Lx86wKkabxSYLDMwYyAhO8eBLQM+O7d8nwA7X7qtD6HV1nsTT2i\n"
    "bEAxnORr0dhjHRD/b+lsritzlwKBgQDV45mQxOhZAErnHN/D0KMG8uDTWCEBVlKt\n"
    "s3aWhlvb4stoax8pt04gLnbo6vctL246LZ7dtxO3sH/vLarpXoXXYgq8TFieRxxl\n"
    "xDA40/SXxU/e+8tzSRIJiZzDLTb6B0M5/LNphhWscTuD7sXraMseXrjMotKF/i4S\n"
    "9IO5wqAaKwKBgHiqgC9Q7sSP426uTsJszQkEQ1u+Hy3kWZezYCoLQkzzK366ARIW\n"
    "AqJ+Z7JY5/Q0ty/i6bAgS551GDknZc6e+UjOXeKRvIg9fWpBkQPyjqN1iFnOs7oi\n"
    "LRIkTOQjc8AjUHwY1C+HCjmPwPsXKViB+vhcr8DzW5ilDD2uKIm/HarZAoGBAIZc\n"
    "WG6B03d9YJA4KjTnDlJiJmt9NBaT9JIbZ4Z9Vp0VpjOs/0GEXfaHWblNSQLAhdzU\n"
    "JbUfuaotnOBR7sh00V0QwK+ywgSDpUokaSp5s2/XyinIQPDl2QfWw3w0HhIIl+mI\n"
    "XegPC/RsmTdyui/8f4RPeoVKTzdPCgBsS4dYxJxLAoGBAMIVAR8NOLYdeIPpoBSI\n"
    "9d3dT3VuwNmBvJNYz9FncvUIFzWxRn02PkqEsYUg2tGhDb9AkZWA8ft4MSOlEBUK\n"
    "cRdBGtIMA3JvMYylb5uexM4FXpFi8cffFFw9GIcUuqZrc8HzGWdjhdrodcUQo86x\n"
    "Jjzz4xpR6mTYMbZZi1VVhask\n"
    "-----END PRIVATE KEY-----\n"
)
TEST_JWK = {
    "kty": "RSA",
    "kid": "test-key-1",
    "use": "sig",
    "alg": "RS256",
    "n": (
        "xV9apzLgqFS_lqhuiWIG9aOOdCMMKhlyBcG3jTw-XEbtYsjz2C0fV23qQUnN9YzF"
        "qNuW_rviyymyC9ZHwyX6EesINK3mHNrJzj_OlvTBI3Arlgvc09MHWvs5Vaylqdwq"
        "3skTnrQq0vZ9myN8MTj68Mt-zk-EE5Vd-LmpSNzB1Ln3JM_GgkwuL-IsGwsBZnmO"
        "hTbxfCrlXMiJBbCHenNDtIkqHibqKjNtm_SpQsS453sCwmKSmRNxCq4bSF10qNqL"
        "peZqhUTQDmdu8EkK8CsyCWN7i-ysyepuxbBA6aAJ3Eso-"
        "rY50vpYlDRlmZX9FNStrkwwjsXlA_lo49TRV2nAXQ"
    ),
    "e": "AQAB",
}


class FakeResponse:
    """Minimal stand-in for an httpx response."""

    def __init__(
        self, payload: Any, *, status: int = 200, error: bool = False
    ) -> None:
        self._payload = payload
        self.status_code = status
        self._error = error

    def raise_for_status(self) -> None:
        if self._error:
            request = httpx.Request("GET", "https://apple.example")
            raise httpx.HTTPStatusError(
                "provider error",
                request=request,
                response=httpx.Response(self.status_code, request=request),
            )

    def json(self) -> Any:
        return self._payload


class FakeClient:
    """Fake async HTTP client recording get/post_retry calls."""

    def __init__(self, factory: FakeClientFactory) -> None:
        self._factory = factory

    async def __aenter__(self) -> FakeClient:  # noqa: PYI034
        return self

    async def __aexit__(self, *exc: object) -> bool:
        return False

    async def get_retry(
        self, url: str, *, headers: dict[str, str] | None = None
    ) -> FakeResponse:
        self._factory.calls.append(
            {"method": "GET", "url": url, "headers": dict(headers or {})}
        )
        return self._factory.routes[("GET", url)].pop(0)

    async def post_retry(
        self,
        url: str,
        *,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> FakeResponse:
        self._factory.calls.append(
            {
                "method": "POST",
                "url": url,
                "data": dict(data or {}),
                "headers": dict(headers or {}),
            }
        )
        return self._factory.routes[("POST", url)].pop(0)


class FakeClientFactory:
    """URL-routed fake responses plus a call log."""

    def __init__(
        self, routes: dict[tuple[str, str], list[FakeResponse]] | None = None
    ) -> None:
        self.routes = {
            key: list(value) for key, value in (routes or {}).items()
        }
        self.calls: list[dict[str, Any]] = []

    def __call__(self) -> FakeClient:
        return FakeClient(self)

    def gets(self, url: str) -> list[dict[str, Any]]:
        return [
            c for c in self.calls if c["method"] == "GET" and c["url"] == url
        ]

    def posts(self, url: str) -> list[dict[str, Any]]:
        return [
            c for c in self.calls if c["method"] == "POST" and c["url"] == url
        ]


def _make_id_token(
    *,
    nonce: str,
    sub: str = "apple-sub-1",
    email: str | None = None,
    name: str | None = None,
    kid: str | None = "test-key-1",
) -> str:
    now = int(time.time())
    claims: dict[str, Any] = {
        "sub": sub,
        "iss": APPLE_ISSUER,
        "aud": CLIENT_ID,
        "iat": now,
        "exp": now + 600,
        "nonce": nonce,
    }
    if email is not None:
        claims["email"] = email
    if name is not None:
        claims["name"] = name
    headers: dict[str, Any] = {"alg": "RS256"}
    if kid is not None:
        headers["kid"] = kid
    return jwt.encode(
        claims, TEST_RSA_PRIVATE_KEY_PEM, algorithm="RS256", headers=headers
    )


def _login(
    cls: type,
    factory: FakeClientFactory,
    *,
    discovery_cache: bool = True,
):
    kwargs: dict[str, Any] = {
        "team_id": TEAM_ID,
        "key_id": KEY_ID,
        "client_id": CLIENT_ID,
        "private_key_pem": SecretBytes(TEST_EC_PRIVATE_KEY_PEM.encode()),
        "redirect_uri": REDIRECT_URI,
        "state_secret": SecretBytes(STATE_SECRET),
    }
    login = cls(**kwargs)
    login._http_client_factory = factory
    if discovery_cache and hasattr(login, "_discovery"):
        login._discovery = dict(METADATA)
    return login


def _assert_client_secret(secret: str) -> dict[str, Any]:
    header = jwt.get_unverified_header(secret)
    assert header["alg"] == "ES256"
    assert header["kid"] == KEY_ID
    claims = jwt.decode(
        secret,
        TEST_EC_PUBLIC_KEY_PEM,
        algorithms=["ES256"],
        audience=APPLE_ISSUER,
    )
    assert claims["iss"] == TEAM_ID
    assert claims["sub"] == CLIENT_ID
    assert claims["aud"] == APPLE_ISSUER
    assert claims["exp"] - claims["iat"] == 180 * 24 * 3600
    return claims


def _assert_auth_url(
    url: str, *, endpoint: str, scope: str
) -> tuple[str, str]:
    parsed = urlsplit(url)
    assert f"{parsed.scheme}://{parsed.netloc}{parsed.path}" == endpoint
    query = parse_qs(parsed.query)
    assert query["response_type"] == ["code"]
    assert query["client_id"] == [CLIENT_ID]
    assert query["redirect_uri"] == [REDIRECT_URI]
    assert query["scope"] == [scope]
    assert query["code_challenge_method"] == ["S256"]
    assert query["code_challenge"]
    assert query["nonce"]
    state = query["state"][0]
    payload = verify_state(STATE_SECRET, state)
    verifier = payload["verifier"]
    assert payload["nonce"] == query["nonce"][0]
    expected_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        .decode()
        .rstrip("=")
    )
    assert query["code_challenge"] == [expected_challenge]
    return state, payload["nonce"]


def _token_routes(
    *,
    token_url: str,
    jwks_url: str,
    id_token: str | None,
    error: bool = False,
) -> dict[tuple[str, str], list[FakeResponse]]:
    payload: dict[str, Any] = {
        "access_token": "apple-access-token",
        "token_type": "Bearer",
        "expires_in": 3600,
    }
    if id_token is not None:
        payload["id_token"] = id_token
    return {
        ("POST", token_url): [
            FakeResponse(payload, status=500 if error else 200, error=error)
        ],
        ("GET", jwks_url): [FakeResponse({"keys": [TEST_JWK]})],
    }


def _assert_token_post(
    factory: FakeClientFactory, *, token_url: str, state: str
) -> dict[str, Any]:
    posts = factory.posts(token_url)
    assert len(posts) == 1
    post = posts[0]
    assert post["headers"] == {"Accept": "application/json"}
    data = post["data"]
    assert data["grant_type"] == "authorization_code"
    assert data["code"] == "auth-code-123"
    assert data["redirect_uri"] == REDIRECT_URI
    assert data["client_id"] == CLIENT_ID
    assert (
        data["code_verifier"] == verify_state(STATE_SECRET, state)["verifier"]
    )
    _assert_client_secret(data["client_secret"])
    return data


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_auth_url_contract() -> None:
    login = _login(AppleOAuth20Login, FakeClientFactory())
    result = await login.auth_url()
    assert set(result) == {"url", "state"}
    returned_state, _ = _assert_auth_url(
        result["url"], endpoint=AUTH_ENDPOINT, scope="name email"
    )
    assert result["state"] == returned_state


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_and_identity() -> None:
    factory = FakeClientFactory()
    login = _login(AppleOAuth20Login, factory)
    state, nonce = _assert_auth_url(
        (await login.auth_url())["url"],
        endpoint=AUTH_ENDPOINT,
        scope="name email",
    )
    id_token = _make_id_token(
        nonce=nonce, email="jane@example.com", name="Jane Doe"
    )
    factory.routes = _token_routes(
        token_url=TOKEN_ENDPOINT, jwks_url=JWKS_URI, id_token=id_token
    )
    result = await login.exchange_and_identity("auth-code-123", state)
    _assert_token_post(factory, token_url=TOKEN_ENDPOINT, state=state)
    assert len(factory.gets(JWKS_URI)) == 1
    assert factory.gets(JWKS_URI)[0]["headers"] == {
        "Accept": "application/json"
    }
    assert result == {
        "issuer": "apple-oauth2",
        "sub": "apple-sub-1",
        "email": "jane@example.com",
        "name": "Jane Doe",
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_nonce_mismatch_raises() -> None:
    factory = FakeClientFactory()
    login = _login(AppleOAuth20Login, factory)
    state, _ = _assert_auth_url(
        (await login.auth_url())["url"],
        endpoint=AUTH_ENDPOINT,
        scope="name email",
    )
    id_token = _make_id_token(nonce="someone-elses-nonce")
    factory.routes = _token_routes(
        token_url=TOKEN_ENDPOINT, jwks_url=JWKS_URI, id_token=id_token
    )
    with pytest.raises(ValueError, match="nonce mismatch"):
        await login.exchange_and_identity("auth-code-123", state)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_missing_id_token_raises() -> None:
    factory = FakeClientFactory()
    login = _login(AppleOAuth20Login, factory)
    state, _ = _assert_auth_url(
        (await login.auth_url())["url"],
        endpoint=AUTH_ENDPOINT,
        scope="name email",
    )
    factory.routes = _token_routes(
        token_url=TOKEN_ENDPOINT, jwks_url=JWKS_URI, id_token=None
    )
    with pytest.raises(ValueError, match="no id_token in response"):
        await login.exchange_and_identity("auth-code-123", state)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_token_http_error_raises() -> None:
    factory = FakeClientFactory()
    login = _login(AppleOAuth20Login, factory)
    state, nonce = _assert_auth_url(
        (await login.auth_url())["url"],
        endpoint=AUTH_ENDPOINT,
        scope="name email",
    )
    id_token = _make_id_token(nonce=nonce)
    factory.routes = _token_routes(
        token_url=TOKEN_ENDPOINT,
        jwks_url=JWKS_URI,
        id_token=id_token,
        error=True,
    )
    with pytest.raises(httpx.HTTPStatusError):
        await login.exchange_and_identity("auth-code-123", state)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_unknown_kid_raises() -> None:
    factory = FakeClientFactory()
    login = _login(AppleOAuth20Login, factory)
    state, nonce = _assert_auth_url(
        (await login.auth_url())["url"],
        endpoint=AUTH_ENDPOINT,
        scope="name email",
    )
    id_token = _make_id_token(nonce=nonce, kid="unknown-key")
    factory.routes = _token_routes(
        token_url=TOKEN_ENDPOINT, jwks_url=JWKS_URI, id_token=id_token
    )
    with pytest.raises(ValueError, match="signing key not found"):
        await login.exchange_and_identity("auth-code-123", state)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_auth_url_uses_discovery() -> None:
    factory = FakeClientFactory(
        {("GET", DISCOVERY_URL): [FakeResponse(dict(METADATA))]}
    )
    login = _login(AppleOAuth21Login, factory, discovery_cache=False)
    result = await login.auth_url()
    assert set(result) == {"url", "state"}
    returned_state, _ = _assert_auth_url(
        result["url"],
        endpoint=METADATA["authorization_endpoint"],
        scope="openid email name",
    )
    assert result["state"] == returned_state
    assert len(factory.gets(DISCOVERY_URL)) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_exchange_and_identity() -> None:
    factory = FakeClientFactory()
    login = _login(AppleOAuth21Login, factory)
    state, nonce = _assert_auth_url(
        (await login.auth_url())["url"],
        endpoint=METADATA["authorization_endpoint"],
        scope="openid email name",
    )
    id_token = _make_id_token(
        nonce=nonce, email="jane@example.com", name="Jane Doe"
    )
    factory.routes = _token_routes(
        token_url=METADATA["token_endpoint"],
        jwks_url=METADATA["jwks_uri"],
        id_token=id_token,
    )
    result = await login.exchange_and_identity("auth-code-123", state)
    _assert_token_post(
        factory, token_url=METADATA["token_endpoint"], state=state
    )
    assert len(factory.gets(METADATA["jwks_uri"])) == 1
    assert result == {
        "issuer": "apple-oauth21",
        "sub": "apple-sub-1",
        "email": "jane@example.com",
        "name": "Jane Doe",
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_discovery_fetched_once() -> None:
    factory = FakeClientFactory(
        {("GET", DISCOVERY_URL): [FakeResponse(dict(METADATA))]}
    )
    login = _login(AppleOAuth21Login, factory, discovery_cache=False)
    state, nonce = _assert_auth_url(
        (await login.auth_url())["url"],
        endpoint=METADATA["authorization_endpoint"],
        scope="openid email name",
    )
    id_token = _make_id_token(nonce=nonce)
    factory.routes.update(
        _token_routes(
            token_url=METADATA["token_endpoint"],
            jwks_url=METADATA["jwks_uri"],
            id_token=id_token,
        )
    )
    await login.exchange_and_identity("auth-code-123", state)
    assert len(factory.gets(DISCOVERY_URL)) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_exchange_missing_id_token_raises() -> None:
    factory = FakeClientFactory()
    login = _login(AppleOAuth21Login, factory)
    state, _ = _assert_auth_url(
        (await login.auth_url())["url"],
        endpoint=METADATA["authorization_endpoint"],
        scope="openid email name",
    )
    factory.routes = _token_routes(
        token_url=METADATA["token_endpoint"],
        jwks_url=METADATA["jwks_uri"],
        id_token=None,
    )
    with pytest.raises(ValueError, match="no id_token in response"):
        await login.exchange_and_identity("auth-code-123", state)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc10_auth_url_uses_discovery() -> None:
    factory = FakeClientFactory(
        {("GET", DISCOVERY_URL): [FakeResponse(dict(METADATA))]}
    )
    login = _login(AppleOIDC10Login, factory, discovery_cache=False)
    result = await login.auth_url()
    returned_state, _ = _assert_auth_url(
        result["url"],
        endpoint=METADATA["authorization_endpoint"],
        scope="openid email name",
    )
    assert result["state"] == returned_state


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc10_exchange() -> None:
    factory = FakeClientFactory()
    login = _login(AppleOIDC10Login, factory)
    state, nonce = _assert_auth_url(
        (await login.auth_url())["url"],
        endpoint=METADATA["authorization_endpoint"],
        scope="openid email name",
    )
    id_token = _make_id_token(
        nonce=nonce, email="jane@example.com", name="Jane Doe"
    )
    factory.routes = _token_routes(
        token_url=METADATA["token_endpoint"],
        jwks_url=METADATA["jwks_uri"],
        id_token=id_token,
    )
    result = await login.exchange("auth-code-123", state)
    _assert_token_post(
        factory, token_url=METADATA["token_endpoint"], state=state
    )
    assert result == {
        "issuer": "apple-oidc",
        "sub": "apple-sub-1",
        "email": "jane@example.com",
        "name": "Jane Doe",
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc10_exchange_nonce_mismatch_raises() -> None:
    factory = FakeClientFactory()
    login = _login(AppleOIDC10Login, factory)
    state, _ = _assert_auth_url(
        (await login.auth_url())["url"],
        endpoint=METADATA["authorization_endpoint"],
        scope="openid email name",
    )
    id_token = _make_id_token(nonce="wrong-nonce")
    factory.routes = _token_routes(
        token_url=METADATA["token_endpoint"],
        jwks_url=METADATA["jwks_uri"],
        id_token=id_token,
    )
    with pytest.raises(ValueError, match="nonce mismatch"):
        await login.exchange("auth-code-123", state)


@pytest.mark.unit
@pytest.mark.parametrize(
    "cls", [AppleOAuth20AppClient, AppleOAuth21AppClient, AppleOIDC10AppClient]
)
@pytest.mark.asyncio
async def test_app_clients_access_token_unsupported(cls: type) -> None:
    client = cls()
    with pytest.raises(NotImplementedError) as excinfo:
        await client.access_token()
    assert "does not issue generic client_credentials" in str(excinfo.value)


@pytest.mark.unit
def test_client_secret_jwt_fields() -> None:
    login = _login(AppleOAuth20Login, FakeClientFactory())
    claims = _assert_client_secret(login._client_secret())
    assert claims["iss"] == TEAM_ID
    assert claims["sub"] == CLIENT_ID
