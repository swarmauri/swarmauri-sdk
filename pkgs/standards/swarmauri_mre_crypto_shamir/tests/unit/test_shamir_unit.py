import asyncio
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy

from swarmauri_mre_crypto_shamir import ShamirMreCrypto


async def _encrypt_decrypt() -> bool:
    crypto = ShamirMreCrypto()
    recips = [
        KeyRef("r1", 1, KeyType.SYMMETRIC, (KeyUse.ENCRYPT,), ExportPolicy.PUBLIC_ONLY),
        KeyRef("r2", 1, KeyType.SYMMETRIC, (KeyUse.ENCRYPT,), ExportPolicy.PUBLIC_ONLY),
        KeyRef("r3", 1, KeyType.SYMMETRIC, (KeyUse.ENCRYPT,), ExportPolicy.PUBLIC_ONLY),
    ]
    env = await crypto.encrypt_for_many(recips, b"unit-test", opts={"threshold_k": 2})
    pt = await crypto.open_for_many(recips[:2], env)
    return pt == b"unit-test"


def test_shamir_encrypt_decrypt_unit():
    assert asyncio.run(_encrypt_decrypt())
