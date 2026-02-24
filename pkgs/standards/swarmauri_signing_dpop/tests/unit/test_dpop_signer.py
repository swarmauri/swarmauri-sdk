import base64
import json
import time
from uuid import uuid4

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_signing_dpop import DpopSigner
from swarmauri_signing_dpop.DpopSigner import _b64url_dec, _jwk_thumbprint_b64url
from swarmauri_signing_jws import JwsSignerVerifier


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
    header = json.loads(_b64url_dec(token.split(".")[0]).decode())
    assert header["typ"] == "dpop+jwt"
    jws = JwsSignerVerifier()
    result = await jws.verify_compact(
        token,
        jwks_resolver=lambda _kid, _alg, jwk=header["jwk"]: jwk,
        alg_allowlist=["EdDSA"],
    )
    claims = json.loads(result.payload.decode())
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
    jws = JwsSignerVerifier()
    token = await jws.sign_compact(
        payload=payload,
        alg="EdDSA",
        key={"kind": "cryptography_obj", "obj": priv},
        header_extra={"jwk": jwk},
        typ="JWT",
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
    jws = JwsSignerVerifier()
    token = await jws.sign_compact(
        payload=payload,
        alg="EdDSA",
        key={"kind": "cryptography_obj", "obj": priv},
        header_extra={"jwk": jwk},
        typ="dpop+jwt",
    )
    signer = DpopSigner()
    assert not await signer.verify_bytes(
        b"",
        [{"sig": token}],
        require={"htm": "GET", "htu": "https://api.example/x"},
    )


@pytest.mark.asyncio
async def test_verify_rejects_wrong_method_or_url() -> None:
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
        require={"htm": "POST", "htu": "https://api.example/x"},
    )
    assert not await signer.verify_bytes(
        b"",
        sigs,
        require={"htm": "GET", "htu": "https://api.example/y"},
    )


@pytest.mark.asyncio
async def test_verify_rejects_skewed_iat() -> None:
    priv = ed25519.Ed25519PrivateKey.generate()
    pem = priv.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    signer = DpopSigner()
    skewed_time = int(time.time()) - 400
    sigs = await signer.sign_bytes(
        {"kind": "pem", "priv": pem, "alg": "EdDSA"},
        b"",
        opts={"htm": "GET", "htu": "https://api.example/x", "iat": skewed_time},
    )
    assert not await signer.verify_bytes(
        b"",
        sigs,
        require={"htm": "GET", "htu": "https://api.example/x", "max_skew_s": 300},
    )


@pytest.mark.asyncio
async def test_verify_requires_expected_nonce() -> None:
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
            "nonce": "nonce-123",
        },
    )
    assert not await signer.verify_bytes(
        b"",
        sigs,
        require={
            "htm": "GET",
            "htu": "https://api.example/x",
            "nonce": "nonce-456",
        },
    )
    assert await signer.verify_bytes(
        b"",
        sigs,
        require={
            "htm": "GET",
            "htu": "https://api.example/x",
            "nonce": "nonce-123",
        },
    )


@pytest.mark.asyncio
async def test_verify_rejects_unapproved_alg() -> None:
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
        require={"htm": "GET", "htu": "https://api.example/x", "algs": ["ES256"]},
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("alg", ["HS256", "HS384", "HS512"])
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


@pytest.mark.asyncio
async def test_sign_rejects_none_alg() -> None:
    signer = DpopSigner()
    keyref = {"kind": "jwk", "priv": {"kty": "oct", "k": "secret"}}
    with pytest.raises(ValueError, match="not a valid JWAAlg"):
        await signer.sign_bytes(
            keyref,
            b"",
            alg="none",
            opts={"htm": "GET", "htu": "https://api.example/x"},
        )
