import asyncio

import pytest

from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_core.keys.types import KeySpec, KeyAlg, KeyClass, ExportPolicy, KeyUse


@pytest.mark.perf
def test_create_performance(benchmark) -> None:
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )

    async def _create() -> None:
        await LocalKeyProvider().create_key(spec)

    benchmark(lambda: asyncio.run(_create()))
