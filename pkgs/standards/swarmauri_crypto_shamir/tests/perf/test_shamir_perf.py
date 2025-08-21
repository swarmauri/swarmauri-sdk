import asyncio
import pytest
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy

from swarmauri_crypto_shamir import ShamirMreCrypto


@pytest.mark.perf
def test_encrypt_perf(benchmark):
    crypto = ShamirMreCrypto()
    recips = [
        KeyRef("r1", 1, KeyType.SYMMETRIC, (KeyUse.ENCRYPT,), ExportPolicy.PUBLIC_ONLY),
        KeyRef("r2", 1, KeyType.SYMMETRIC, (KeyUse.ENCRYPT,), ExportPolicy.PUBLIC_ONLY),
        KeyRef("r3", 1, KeyType.SYMMETRIC, (KeyUse.ENCRYPT,), ExportPolicy.PUBLIC_ONLY),
    ]

    async def _enc():
        await crypto.encrypt_for_many(recips, b"perf", opts={"threshold_k": 2})

    benchmark(lambda: asyncio.run(_enc()))
