import asyncio

from pgpy import PGPKey, PGPUID
from pgpy.constants import (
    CompressionAlgorithm,
    HashAlgorithm,
    KeyFlags,
    PubKeyAlgorithm,
    SymmetricKeyAlgorithm,
)

from swarmauri_signing_pgp import PgpEnvelopeSigner


def make_demo_key() -> PGPKey:
    key = PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048)
    uid = PGPUID.new("Example User", email="user@example.com")
    key.add_uid(
        uid,
        usage={KeyFlags.Sign},
        hashes=[HashAlgorithm.SHA256],
        ciphers=[SymmetricKeyAlgorithm.AES256],
        compression=[CompressionAlgorithm.ZLIB],
    )
    return key


async def main() -> None:
    signer = PgpEnvelopeSigner()
    key = make_demo_key()
    key_ref = {"kind": "pgpy_key", "priv": key}
    payload = b"openpgp demo"

    signatures = await signer.sign_bytes(key_ref, payload)
    verified = await signer.verify_bytes(
        payload,
        signatures,
        opts={"pubkeys": [key.pubkey]},
    )
    print("Verified:", verified)


asyncio.run(main())
