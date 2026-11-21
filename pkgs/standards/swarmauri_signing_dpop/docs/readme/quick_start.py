import asyncio

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_signing_dpop import DpopSigner


async def main() -> None:
    signer = DpopSigner()

    private_key = ed25519.Ed25519PrivateKey.generate()
    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    key = {"kind": "pem", "priv": priv_pem, "alg": "EdDSA"}

    signatures = await signer.sign_bytes(
        key,
        b"",
        opts={"htm": "GET", "htu": "https://api.example/x"},
    )

    is_valid = await signer.verify_bytes(
        b"",
        signatures,
        require={"htm": "GET", "htu": "https://api.example/x"},
    )
    assert is_valid
    print("DPoP proof valid:", is_valid)


asyncio.run(main())
