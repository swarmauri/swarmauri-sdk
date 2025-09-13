import base64
import time
from uuid import uuid4

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_signing_dpop import DpopSigner
from swarmauri_signing_dpop.DpopSigner import _jwk_thumbprint_b64url


@pytest.mark.asyncio
async def test_sign_and_verify_dpop() -> None:
    priv = ed25519.Ed25519PrivateKey.generate()
    pem = priv.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    keyref = {"kind": "pem", "priv": pem, "alg": "EdDSA"}
    signer = DpopSigner()
    sigs = await signer.sign_bytes(
        keyref,
        b"",
        opts={"htm": "GET", "htu": "https://api.example/x"},
    )
    assert await signer.verify_bytes(
        b"",
        sigs,
        require={"htm": "GET", "htu": "https://api.example/x"},
    )


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


@pytest.mark.asyncio
async def test_proof_contains_required_header_and_claims() -> None:
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
        opts={"htm": "POST", "htu": "https://api.example/resource"},
    )
    token = sigs[0]["sig"]
    header = jwt.get_unverified_header(token)
    assert header["typ"] == "dpop+jwt"
    claims = jwt.decode(
        token,
        priv.public_key(),
        algorithms=["EdDSA"],
        options={"verify_aud": False, "verify_exp": False},
    )
    for field in ("htm", "htu", "iat", "jti"):
        assert field in claims
    assert claims["htm"] == "POST"
    assert claims["htu"] == "https://api.example/resource"
    assert sigs[0]["jkt"] == _jwk_thumbprint_b64url(header["jwk"])


@pytest.mark.asyncio
async def test_verify_rejects_proof_with_wrong_typ() -> None:
    priv = ed25519.Ed25519PrivateKey.generate()
    pub = priv.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    jwk = {"kty": "OKP", "crv": "Ed25519", "x": _b64u(pub)}
    payload = {
        "htm": "GET",
        "htu": "https://api.example/x",
        "iat": int(time.time()),
        "jti": str(uuid4()),
    }
    token = jwt.encode(
        payload,
        priv,
        algorithm="EdDSA",
        headers={"typ": "JWT", "jwk": jwk},
    )
    signer = DpopSigner()
    assert not await signer.verify_bytes(
        b"",
        [{"sig": token}],
        require={"htm": "GET", "htu": "https://api.example/x"},
    )


@pytest.mark.asyncio
async def test_verify_rejects_proof_missing_jti() -> None:
    priv = ed25519.Ed25519PrivateKey.generate()
    pub = priv.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    jwk = {"kty": "OKP", "crv": "Ed25519", "x": _b64u(pub)}
    payload = {
        "htm": "GET",
        "htu": "https://api.example/x",
        "iat": int(time.time()),
    }  # missing jti
    token = jwt.encode(
        payload,
        priv,
        algorithm="EdDSA",
        headers={"typ": "dpop+jwt", "jwk": jwk},
    )
    signer = DpopSigner()
    assert not await signer.verify_bytes(
        b"",
        [{"sig": token}],
        require={"htm": "GET", "htu": "https://api.example/x"},
    )

@pytest.mark.asyncio
@pytest.mark.parametrize("alg", ["HS256", "HS384", "HS512", "none"])
async def test_sign_rejects_unsupported_algs(alg: str) -> None:
    signer = DpopSigner()
    keyref = {"kind": "jwk", "priv": {"kty": "oct", "k": "secret"}}
    with pytest.raises(ValueError, match="Unsupported alg"):
        await signer.sign_bytes(
            keyref,
            b"",
            alg=alg,
            opts={"htm": "GET", "htu": "https://api.example/x"},
        )
