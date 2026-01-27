import asyncio
import pytest

from swarmauri_keyprovider_hierarchical import HierarchicalKeyProvider
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_core.key_providers.types import (
    KeySpec,
    KeyAlg,
    KeyClass,
    ExportPolicy,
    KeyUse,
)


@pytest.mark.test
@pytest.mark.perf
def test_create_performance(benchmark) -> None:
    child = LocalKeyProvider()
    provider = HierarchicalKeyProvider({"a": child})
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )

    def run() -> None:
        asyncio.run(provider.create_key(spec))

    benchmark(run)
