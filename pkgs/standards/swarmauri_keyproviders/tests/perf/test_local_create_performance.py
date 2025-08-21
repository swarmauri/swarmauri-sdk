import asyncio

import pytest

from swarmauri_keyproviders import LocalKeyProvider
from swarmauri_core.keys.types import KeySpec, KeyAlg, KeyClass, ExportPolicy, KeyUse


@pytest.mark.perf
def test_create_performance(benchmark) -> None:
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )

    def run() -> None:
        asyncio.run(LocalKeyProvider().create_key(spec))

    benchmark(run)
