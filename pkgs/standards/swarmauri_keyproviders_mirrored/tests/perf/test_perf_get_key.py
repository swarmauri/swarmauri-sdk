import pytest

from swarmauri_core.key_providers.types import ExportPolicy, KeyAlg, KeyClass, KeySpec
import asyncio
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_keyproviders_mirrored import MirroredKeyProvider


@pytest.mark.perf
def test_get_key_performance(benchmark) -> None:
    primary = LocalKeyProvider()
    secondary = LocalKeyProvider()
    provider = MirroredKeyProvider(primary, secondary, mirror_mode="full")
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        size_bits=None,
        label="perf",
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        uses=(),
    )
    pref = asyncio.run(provider.create_key(spec))

    def run() -> None:
        asyncio.run(provider.get_key(pref.kid, pref.version))

    benchmark(run)
