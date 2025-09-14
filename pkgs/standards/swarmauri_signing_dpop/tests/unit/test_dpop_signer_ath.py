import json

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_signing_dpop import DpopSigner
from swarmauri_signing_dpop.DpopSigner import _ath_from_access_token, _b64url_dec
from swarmauri_signing_jws import JwsSignerVerifier


@pytest.mark.asyncio
async def test_sign_and_verify_with_ath() -> None:
    priv = ed25519.Ed25519PrivateKey.generate()
    pem = priv.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    signer = DpopSigner()
    access_token = "Bearer abc123"
    sigs = await signer.sign_bytes(
        {"kind": "pem", "priv": pem, "alg": "EdDSA"},
        b"",
        opts={
            "htm": "GET",
            "htu": "https://api.example/x",
            "access_token": access_token,
        },
    )
    token = sigs[0]["sig"]
    header = json.loads(_b64url_dec(token.split(".")[0]).decode())
    jws = JwsSignerVerifier()
    result = await jws.verify_compact(
        token,
        jwks_resolver=lambda _kid, _alg, jwk=header["jwk"]: jwk,
        alg_allowlist=["EdDSA"],
    )
    claims = json.loads(result.payload.decode())
    assert claims["ath"] == _ath_from_access_token(access_token)
    assert await signer.verify_bytes(
        b"",
        sigs,
        require={
            "htm": "GET",
            "htu": "https://api.example/x",
            "access_token": access_token,
        },
    )


@pytest.mark.asyncio
async def test_verify_fails_missing_ath_when_expected() -> None:
    priv = ed25519.Ed25519PrivateKey.generate()
    pem = priv.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    signer = DpopSigner()
    sigs = await signer.sign_bytes(
        {"kind": "pem", "priv": pem, "alg": "EdDSA"},
        b"",
        opts={"htm": "GET", "htu": "https://api.example/x"},
    )
    assert not await signer.verify_bytes(
        b"",
        sigs,
        require={
            "htm": "GET",
            "htu": "https://api.example/x",
            "access_token": "Bearer abc123",
        },
    )


@pytest.mark.asyncio
async def test_verify_fails_with_wrong_access_token() -> None:
    priv = ed25519.Ed25519PrivateKey.generate()
    pem = priv.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    signer = DpopSigner()
    sigs = await signer.sign_bytes(
        {"kind": "pem", "priv": pem, "alg": "EdDSA"},
        b"",
        opts={
            "htm": "GET",
            "htu": "https://api.example/x",
            "access_token": "Bearer token1",
        },
    )
    assert not await signer.verify_bytes(
        b"",
        sigs,
        require={
            "htm": "GET",
            "htu": "https://api.example/x",
            "access_token": "Bearer token2",
        },
    )
