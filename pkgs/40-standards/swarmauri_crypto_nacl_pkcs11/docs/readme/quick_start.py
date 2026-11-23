import asyncio

from swarmauri_crypto_nacl_pkcs11 import NaClPkcs11Crypto
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


async def main() -> None:
    crypto = NaClPkcs11Crypto()

    symmetric_key = KeyRef(
        kid="sym1",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"\x00" * 32,
    )

    ciphertext = await crypto.encrypt(symmetric_key, b"hello")
    plaintext = await crypto.decrypt(symmetric_key, ciphertext)
    assert plaintext == b"hello"


asyncio.run(main())
