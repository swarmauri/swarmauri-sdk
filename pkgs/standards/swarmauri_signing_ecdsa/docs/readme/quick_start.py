import asyncio
from cryptography.hazmat.primitives.asymmetric import ec

from swarmauri_signing_ecdsa import EcdsaEnvelopeSigner


async def main() -> None:
    signer = EcdsaEnvelopeSigner()

    # Provide the private key as a KeyRef understood by swarmauri_core
    private_key = ec.generate_private_key(ec.SECP256R1())
    key_ref = {"kind": "cryptography_obj", "obj": private_key}

    envelope = {
        "headers": {"kid": "example"},
        "payload": {"message": "signed hello"},
    }

    signatures = await signer.sign_envelope(
        key_ref,
        envelope,
        canon="json",
    )

    is_valid = await signer.verify_envelope(
        envelope,
        signatures,
        canon="json",
        opts={"pubkeys": [private_key.public_key()]},
    )

    print(f"Signature valid? {is_valid}")


if __name__ == "__main__":
    asyncio.run(main())
