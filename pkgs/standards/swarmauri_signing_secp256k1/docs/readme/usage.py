import asyncio

from cryptography.hazmat.primitives.asymmetric import ec

from swarmauri_signing_secp256k1 import Secp256k1EnvelopeSigner


async def main() -> bool:
    signer = Secp256k1EnvelopeSigner()

    private_key = ec.generate_private_key(ec.SECP256K1())
    key_ref = {"kind": "cryptography_obj", "obj": private_key}

    payload = b"hello from secp256k1"
    signatures = await signer.sign_bytes(key_ref, payload)

    public_key_ref = {
        "kind": "cryptography_obj",
        "obj": private_key.public_key(),
    }
    is_valid = await signer.verify_bytes(
        payload,
        signatures,
        opts={"pubkeys": [public_key_ref]},
    )

    print(f"Signature valid? {is_valid}")
    assert is_valid
    return is_valid


if __name__ == "__main__":
    asyncio.run(main())
