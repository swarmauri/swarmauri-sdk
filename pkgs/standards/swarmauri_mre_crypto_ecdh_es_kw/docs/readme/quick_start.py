import asyncio

from cryptography.hazmat.primitives.asymmetric import ec

from swarmauri_mre_crypto_ecdh_es_kw import EcdhEsA128KwMreCrypto


async def main() -> None:
    crypto = EcdhEsA128KwMreCrypto()

    sk = ec.generate_private_key(ec.SECP256R1())
    pk = sk.public_key()
    recipient = {
        "kid": "1",
        "version": 1,
        "kind": "cryptography_obj",
        "obj": pk,
    }

    envelope = await crypto.encrypt_for_many(
        [recipient], b"secret", aad=b"metadata"
    )
    plaintext = await crypto.open_for(
        {"kind": "cryptography_obj", "obj": sk}, envelope, aad=b"metadata"
    )

    assert plaintext == b"secret"


if __name__ == "__main__":
    asyncio.run(main())
