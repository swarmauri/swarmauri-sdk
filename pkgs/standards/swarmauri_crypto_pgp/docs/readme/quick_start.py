import asyncio

from swarmauri_crypto_pgp import PGPCrypto
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


async def main() -> None:
    crypto = PGPCrypto()

    # Symmetric key for AES-256-GCM
    sym = KeyRef(
        kid="sym1",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"\x00" * 32,
    )

    ct = await crypto.encrypt(sym, b"hello OpenPGP")
    pt = await crypto.decrypt(sym, ct)

    print(pt)


if __name__ == "__main__":
    asyncio.run(main())
