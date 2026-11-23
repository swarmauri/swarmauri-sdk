"""Unit tests for the Cognito ID-token algorithm allowlist (#6279).

``CognitoLoginMixin._decode_id_token`` must only accept ID tokens signed
with an algorithm from the implementation-owned allowlist (RS256, the only
algorithm Amazon Cognito user pools use to sign ID tokens). The allowlist
is never taken from the token's unverified ``alg`` header, so tokens that
claim an unsupported algorithm, claim no algorithm, or are unsigned are
rejected before signature verification.

Everything runs offline: the JWKS endpoint is stubbed to serve a local
throwaway RSA key, and the tokens are minted with that key. No network
access, credentials, or live Cognito account are needed, and nothing here
proves interoperability with Cognito's production service.
"""

from __future__ import annotations

import base64
import json
import time
from collections.abc import Mapping
from secrets import token_bytes
from typing import Any

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_cognito import CognitoOIDC10Login

ISSUER = "https://cognito.example"
CLIENT_ID = "client"
JWKS_URI = "https://cognito.example/jwks"

KEY_ID = "test-key-1"


@pytest.fixture(scope="module")
def signing_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(scope="module")
def private_key_pem(signing_key: rsa.RSAPrivateKey) -> bytes:
    return signing_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )


@pytest.fixture(scope="module")
def jwks(signing_key: rsa.RSAPrivateKey) -> dict[str, Any]:
    jwk = json.loads(
        jwt.algorithms.RSAAlgorithm.to_jwk(signing_key.public_key())
    )
    jwk.update(kid=KEY_ID, use="sig", alg="RS256")
    return {"keys": [jwk]}


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _claims(**overrides: Any) -> dict[str, Any]:
    now = int(time.time())
    claims = {
        "sub": "user-123",
        "email": "user@example.com",
        "iss": ISSUER,
        "aud": CLIENT_ID,
        "iat": now,
        "exp": now + 3600,
    }
    claims.update(overrides)
    return claims


def _mint_token(
    key: bytes | str | None, *, algorithm: str = "RS256", **claims: Any
) -> str:
    return jwt.encode(
        _claims(**claims),
        key,
        algorithm=algorithm,
        headers={"kid": KEY_ID},
    )


def _mint_token_without_alg() -> str:
    header = _b64url(json.dumps({"kid": KEY_ID, "typ": "JWT"}).encode("utf-8"))
    payload = _b64url(json.dumps(_claims()).encode("utf-8"))
    return f"{header}.{payload}."


@pytest.fixture
def login() -> CognitoOIDC10Login:
    instance = CognitoOIDC10Login(
        issuer=ISSUER,
        client_id=CLIENT_ID,
        client_secret=SecretStr("secret"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"state-secret"),
    )
    instance._discovery = {
        "authorization_endpoint": "https://cognito.example/authorize",
        "token_endpoint": "https://cognito.example/token",
        "jwks_uri": JWKS_URI,
    }
    return instance


@pytest.fixture
def stubbed_jwks(
    login: CognitoOIDC10Login, jwks: dict[str, Any]
) -> CognitoOIDC10Login:
    async def fake_http_get(
        url: str, *, headers: Mapping[str, str] | None = None
    ) -> Mapping[str, Any]:
        assert url == JWKS_URI
        return jwks

    login._http_get = fake_http_get  # type: ignore[method-assign]
    return login


@pytest.mark.unit
@pytest.mark.asyncio
async def test_valid_rs256_token_decodes(
    stubbed_jwks: CognitoOIDC10Login,
    private_key_pem: bytes,
) -> None:
    token = _mint_token(private_key_pem)
    claims = await stubbed_jwks._decode_id_token(
        token,
        jwks_uri=JWKS_URI,
        expected_audience=CLIENT_ID,
        issuer=ISSUER,
    )
    assert claims["sub"] == "user-123"
    assert claims["email"] == "user@example.com"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_hs256_token_rejected(stubbed_jwks: CognitoOIDC10Login) -> None:
    token = _mint_token(algorithm="HS256", key=token_bytes(32))
    with pytest.raises(ValueError, match="unsupported id_token"):
        await stubbed_jwks._decode_id_token(
            token,
            jwks_uri=JWKS_URI,
            expected_audience=CLIENT_ID,
            issuer=ISSUER,
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_unsigned_token_rejected(
    stubbed_jwks: CognitoOIDC10Login,
) -> None:
    token = _mint_token(algorithm="none", key=None)
    with pytest.raises(ValueError, match="unsupported id_token"):
        await stubbed_jwks._decode_id_token(
            token,
            jwks_uri=JWKS_URI,
            expected_audience=CLIENT_ID,
            issuer=ISSUER,
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_missing_alg_rejected(stubbed_jwks: CognitoOIDC10Login) -> None:
    token = _mint_token_without_alg()
    with pytest.raises(ValueError, match="missing alg"):
        await stubbed_jwks._decode_id_token(
            token,
            jwks_uri=JWKS_URI,
            expected_audience=CLIENT_ID,
            issuer=ISSUER,
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_missing_kid_rejected(
    stubbed_jwks: CognitoOIDC10Login,
    private_key_pem: bytes,
) -> None:
    token = jwt.encode(
        _claims(),
        private_key_pem,
        algorithm="RS256",
        headers={"typ": "JWT"},
    )
    with pytest.raises(ValueError, match="missing kid"):
        await stubbed_jwks._decode_id_token(
            token,
            jwks_uri=JWKS_URI,
            expected_audience=CLIENT_ID,
            issuer=ISSUER,
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_expired_token_rejected(
    stubbed_jwks: CognitoOIDC10Login,
    private_key_pem: bytes,
) -> None:
    token = _mint_token(private_key_pem, exp=int(time.time()) - 60)
    with pytest.raises(jwt.ExpiredSignatureError):
        await stubbed_jwks._decode_id_token(
            token,
            jwks_uri=JWKS_URI,
            expected_audience=CLIENT_ID,
            issuer=ISSUER,
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_wrong_audience_rejected(
    stubbed_jwks: CognitoOIDC10Login,
    private_key_pem: bytes,
) -> None:
    token = _mint_token(private_key_pem, aud="other-client")
    with pytest.raises(jwt.InvalidAudienceError):
        await stubbed_jwks._decode_id_token(
            token,
            jwks_uri=JWKS_URI,
            expected_audience=CLIENT_ID,
            issuer=ISSUER,
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_wrong_issuer_rejected(
    stubbed_jwks: CognitoOIDC10Login,
    private_key_pem: bytes,
) -> None:
    token = _mint_token(private_key_pem, iss="https://cognito.other")
    with pytest.raises(jwt.InvalidIssuerError):
        await stubbed_jwks._decode_id_token(
            token,
            jwks_uri=JWKS_URI,
            expected_audience=CLIENT_ID,
            issuer=ISSUER,
        )
