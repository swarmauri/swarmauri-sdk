import asyncio
from cryptography.hazmat.primitives.asymmetric import ed25519
from swarmauri_signing_pep458 import Pep458Signer


async def main() -> None:
    signer = Pep458Signer()
    private = ed25519.Ed25519PrivateKey.generate()
    keyref = {"kind": "cryptography_obj", "obj": private, "alg": "Ed25519"}

    payload = b"release metadata"
    signatures = await signer.sign_bytes(keyref, payload)

    is_valid = await signer.verify_bytes(
        payload,
        signatures,
        opts={"pubkeys": [private.public_key()]},
    )
    print(f"Signature valid? {is_valid}")


asyncio.run(main())
