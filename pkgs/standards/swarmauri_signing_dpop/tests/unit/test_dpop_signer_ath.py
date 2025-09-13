import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_signing_dpop import DpopSigner
from swarmauri_signing_dpop.DpopSigner import _ath_from_access_token


@pytest.mark.asyncio
async def test_signer_includes_ath_when_access_token_provided() -> None:
    priv = ed25519.Ed25519PrivateKey.generate()
    pem = priv.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    access_token = "Bearer access-token"
    signer = DpopSigner()
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
    claims = jwt.decode(
        token,
        priv.public_key(),
        algorithms=["EdDSA"],
        options={"verify_aud": False, "verify_exp": False},
    )
    assert claims["ath"] == _ath_from_access_token(access_token)


@pytest.mark.asyncio
async def test_verify_enforces_access_token_hash_binding() -> None:
    priv = ed25519.Ed25519PrivateKey.generate()
    pem = priv.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    signer = DpopSigner()
    access_token = "Bearer supersecret"
    sigs = await signer.sign_bytes(
        {"kind": "pem", "priv": pem, "alg": "EdDSA"},
        b"",
        opts={
            "htm": "POST",
            "htu": "https://api.example/resource",
            "access_token": access_token,
        },
    )
    assert await signer.verify_bytes(
        b"",
        sigs,
        require={
            "htm": "POST",
            "htu": "https://api.example/resource",
            "access_token": access_token,
        },
    )
    assert not await signer.verify_bytes(
        b"",
        sigs,
        require={
            "htm": "POST",
            "htu": "https://api.example/resource",
            "access_token": "Bearer other",
        },
    )


@pytest.mark.asyncio
async def test_verify_rejects_missing_ath_when_access_token_required() -> None:
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
            "access_token": "Bearer needs-ath",
        },
    )
