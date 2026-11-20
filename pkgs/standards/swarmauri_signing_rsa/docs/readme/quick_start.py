import asyncio

from cryptography.hazmat.primitives.asymmetric import rsa

from swarmauri_signing_rsa import RSAEnvelopeSigner


def key_ref_from_private(private_key):
    return {"kind": "cryptography_obj", "obj": private_key}


def key_ref_from_public(public_key):
    return {"kind": "cryptography_obj", "obj": public_key}


async def main() -> None:
    signer = RSAEnvelopeSigner()
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048
    )

    envelope = {
        "payload": {"msg": "hello"},
        "headers": {"alg": "RSA-PSS-SHA256"},
    }

    signatures = await signer.sign_envelope(
        key_ref_from_private(private_key),
        envelope,
        canon="json",
        alg="RSA-PSS-SHA256",
    )

    is_valid = await signer.verify_envelope(
        envelope,
        signatures,
        opts={"pubkeys": [key_ref_from_public(private_key.public_key())]},
    )

    assert is_valid


asyncio.run(main())
