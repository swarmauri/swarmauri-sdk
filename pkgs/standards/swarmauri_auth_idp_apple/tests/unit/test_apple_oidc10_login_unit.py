import base64
import json
import time

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from pydantic import SecretBytes

from swarmauri_auth_idp_apple import AppleOIDC10Login
from swarmauri_auth_idp_apple.internal.client_secret import (
    AppleClientSecretFactory,
)
from swarmauri_auth_idp_apple.internal.login_base import ID_TOKEN_ALGORITHMS


@pytest.fixture
def login() -> AppleOIDC10Login:
    instance = AppleOIDC10Login(
        team_id="team",
        key_id="key",
        client_id="client",
        private_key_pem=SecretBytes(b"dummy"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"state-secret"),
    )
    instance._discovery = {
        "authorization_endpoint": "https://apple.example/authorize",
        "token_endpoint": "https://apple.example/token",
        "jwks_uri": "https://apple.example/keys",
    }
    return instance


@pytest.mark.unit
def test_resource(login: AppleOIDC10Login) -> None:
    assert login.resource == "OIDC10Login"


@pytest.mark.unit
def test_type(login: AppleOIDC10Login) -> None:
    assert login.type == "AppleOIDC10Login"


@pytest.mark.unit
def test_initialization(login: AppleOIDC10Login) -> None:
    assert isinstance(login.id, str)


@pytest.mark.unit
def test_serialization(login: AppleOIDC10Login) -> None:
    serialized = login.model_dump_json()
    data = json.loads(serialized)

    restored = AppleOIDC10Login.model_construct(**data)
    restored.private_key_pem = login.private_key_pem
    restored.state_secret = login.state_secret
    restored._discovery = login._discovery

    assert restored.id == login.id
    assert restored.resource == login.resource
    assert restored.type == login.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_uses_discovery(login: AppleOIDC10Login) -> None:
    payload = await login.auth_url()
    assert payload["url"].startswith("https://apple.example/authorize?")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_invalid_state(login: AppleOIDC10Login) -> None:
    with pytest.raises(ValueError):
        await login.exchange("code", "invalid-state")


# --- ID-token algorithm allowlist (issue #6273) ---


def _b64url_int(value: int) -> str:
    raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _b64url_json(payload) -> str:
    raw = json.dumps(payload, separators=(",", ":")).encode()
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


_UNSET = object()


def _mint_token(rsa_key, *, alg="RS256", key=_UNSET, **overrides):
    now = int(time.time())
    payload = {
        "iss": "https://appleid.apple.com",
        "aud": "client",
        "sub": "user-123",
        "exp": now + 600,
        "iat": now,
        "nonce": "test-nonce",
    }
    payload.update(overrides)
    signing_key = rsa_key if key is _UNSET else key
    return jwt.encode(
        payload, signing_key, algorithm=alg, headers={"kid": "test-key"}
    )


async def _decode(login, token, jwks, *, nonce="test-nonce"):
    async def fake_http_get(url: str):
        assert url == "https://apple.example/keys"
        return jwks

    login._http_get = fake_http_get
    return await login._decode_identity(
        token,
        nonce=nonce,
        jwks_uri="https://apple.example/keys",
        expected_audience="client",
    )


@pytest.mark.unit
def test_id_token_algorithms_are_provider_owned() -> None:
    assert ID_TOKEN_ALGORITHMS == ("RS256",)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_decode_identity_accepts_rs256_token(
    login: AppleOIDC10Login, rsa_key, jwks
) -> None:
    token = _mint_token(rsa_key)
    claims = await _decode(login, token, jwks)
    assert claims["sub"] == "user-123"
    assert claims["nonce"] == "test-nonce"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_decode_identity_rejects_hs256_token(
    login: AppleOIDC10Login, rsa_key, jwks
) -> None:
    token = _mint_token(rsa_key, alg="HS256", key=b"shared-secret")
    with pytest.raises(
        ValueError, match="unsupported id_token signing algorithm"
    ):
        await _decode(login, token, jwks)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_decode_identity_rejects_unsigned_token(
    login: AppleOIDC10Login, rsa_key, jwks
) -> None:
    token = _mint_token(rsa_key, alg="none", key=None)
    with pytest.raises(
        ValueError, match="unsupported id_token signing algorithm"
    ):
        await _decode(login, token, jwks)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_decode_identity_rejects_missing_alg(
    login: AppleOIDC10Login, rsa_key, jwks
) -> None:
    now = int(time.time())
    payload = {
        "iss": "https://appleid.apple.com",
        "aud": "client",
        "sub": "user-123",
        "exp": now + 600,
        "iat": now,
        "nonce": "test-nonce",
    }
    token = _b64url_json({"kid": "test-key"}) + "." + _b64url_json(payload)
    token += "."
    with pytest.raises(
        ValueError, match="unsupported id_token signing algorithm"
    ):
        await _decode(login, token, jwks)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_decode_identity_rejects_expired_token(
    login: AppleOIDC10Login, rsa_key, jwks
) -> None:
    token = _mint_token(rsa_key, exp=int(time.time()) - 10)
    with pytest.raises(jwt.ExpiredSignatureError):
        await _decode(login, token, jwks)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_decode_identity_rejects_nonce_mismatch(
    login: AppleOIDC10Login, rsa_key, jwks
) -> None:
    token = _mint_token(rsa_key, nonce="other-nonce")
    with pytest.raises(ValueError, match="nonce mismatch"):
        await _decode(login, token, jwks)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_decode_identity_rejects_wrong_audience(
    login: AppleOIDC10Login, rsa_key, jwks
) -> None:
    token = _mint_token(rsa_key, aud="other-client")
    with pytest.raises(jwt.InvalidAudienceError):
        await _decode(login, token, jwks)


@pytest.mark.unit
def test_client_secret_signing_stays_es256() -> None:
    """Client-secret signing (ES256) stays separate from ID-token
    verification (RS256): the two algorithm domains must not be mixed."""

    private_key = ec.generate_private_key(ec.SECP256R1())
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    secret = AppleClientSecretFactory(
        team_id="team",
        key_id="key",
        client_id="client",
        private_key_pem=private_pem,
    ).build()
    assert jwt.get_unverified_header(secret)["alg"] == "ES256"
    assert "ES256" not in ID_TOKEN_ALGORITHMS
