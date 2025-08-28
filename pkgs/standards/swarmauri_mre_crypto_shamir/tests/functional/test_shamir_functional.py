import asyncio
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy

from swarmauri_mre_crypto_shamir import ShamirMreCrypto


async def _run() -> bool:
    crypto = ShamirMreCrypto()
    r1 = KeyRef("r1", 1, KeyType.SYMMETRIC, (KeyUse.ENCRYPT,), ExportPolicy.PUBLIC_ONLY)
    r2 = KeyRef("r2", 1, KeyType.SYMMETRIC, (KeyUse.ENCRYPT,), ExportPolicy.PUBLIC_ONLY)
    r3 = KeyRef("r3", 1, KeyType.SYMMETRIC, (KeyUse.ENCRYPT,), ExportPolicy.PUBLIC_ONLY)
    env = await crypto.encrypt_for_many(
        [r1, r2, r3], b"functional", opts={"threshold_k": 2}
    )
    r4 = KeyRef("r4", 1, KeyType.SYMMETRIC, (KeyUse.ENCRYPT,), ExportPolicy.PUBLIC_ONLY)
    env2 = await crypto.rewrap(env, add=[r4], remove=["r1"])
    pt = await crypto.open_for_many([r2, r3, r4], env2)
    return pt == b"functional"


def test_rewrap_functional():
    assert asyncio.run(_run())
