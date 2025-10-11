import asyncio
import pytest

from swarmauri_keyprovider_file import FileKeyProvider
from swarmauri_core.key_providers.types import KeySpec, KeyClass, KeyAlg, ExportPolicy
from swarmauri_core.crypto.types import KeyUse


@pytest.mark.test
@pytest.mark.perf
def test_key_generation_perf(benchmark, tmp_path):
    provider = FileKeyProvider(tmp_path)
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )

    def create():
        asyncio.run(provider.create_key(spec))

    benchmark(create)
