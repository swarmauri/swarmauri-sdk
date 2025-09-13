import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_signing_dpop import DpopSigner


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
