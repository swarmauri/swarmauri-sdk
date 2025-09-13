import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_signing_dpop import DpopSigner
from swarmauri_signing_dpop.DpopSigner import _ath_from_access_token


@pytest.mark.asyncio
async def test_sign_includes_ath_when_access_token_provided() -> None:
    priv = ed25519.Ed25519PrivateKey.generate()
    pem = priv.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    signer = DpopSigner()
    token = "Bearer abc123"
    sigs = await signer.sign_bytes(
        {"kind": "pem", "priv": pem, "alg": "EdDSA"},
        b"",
        opts={
            "htm": "GET",
            "htu": "https://api.example/x",
            "access_token": token,
        },
    )
    proof = sigs[0]["sig"]
    claims = jwt.decode(
        proof,
        priv.public_key(),
        algorithms=["EdDSA"],
        options={"verify_aud": False, "verify_exp": False},
    )
    assert claims["ath"] == _ath_from_access_token(token)


@pytest.mark.asyncio
async def test_verify_succeeds_with_matching_access_token() -> None:
    priv = ed25519.Ed25519PrivateKey.generate()
    pem = priv.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    signer = DpopSigner()
    token = "Bearer token-xyz"
    sigs = await signer.sign_bytes(
        {"kind": "pem", "priv": pem, "alg": "EdDSA"},
        b"",
        opts={
            "htm": "POST",
            "htu": "https://api.example/resource",
            "access_token": token,
        },
    )
    assert await signer.verify_bytes(
        b"",
        sigs,
        require={
            "htm": "POST",
            "htu": "https://api.example/resource",
            "access_token": token,
        },
    )


@pytest.mark.asyncio
async def test_verify_rejects_with_wrong_access_token() -> None:
    priv = ed25519.Ed25519PrivateKey.generate()
    pem = priv.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    signer = DpopSigner()
    good_token = "Bearer correct"
    sigs = await signer.sign_bytes(
        {"kind": "pem", "priv": pem, "alg": "EdDSA"},
        b"",
        opts={
            "htm": "PUT",
            "htu": "https://api.example/other",
            "access_token": good_token,
        },
    )
    assert not await signer.verify_bytes(
        b"",
        sigs,
        require={
            "htm": "PUT",
            "htu": "https://api.example/other",
            "access_token": "Bearer wrong",
        },
    )
