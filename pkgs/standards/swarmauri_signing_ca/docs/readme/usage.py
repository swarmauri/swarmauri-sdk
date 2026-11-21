import asyncio

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse
from swarmauri_signing_ca import CASigner


async def main() -> None:
    signer = CASigner()

    private_key = ed25519.Ed25519PrivateKey.generate()
    key_ref = KeyRef(
        kid="demo-ed25519",
        version=1,
        type=KeyType.ED25519,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ),
    )

    message = b"trust but verify"
    signatures = await signer.sign_bytes(key_ref, message)
    signature = signatures[0]

    verified = await signer.verify_bytes(
        message,
        signatures,
        opts={"pubkeys": [private_key.public_key()]},
    )

    print("Signature algorithm:", signature["alg"])
    print("Key fingerprint:", key_ref.fingerprint)
    print("Signature valid:", verified)

    assert verified is True


if __name__ == "__main__":
    asyncio.run(main())
