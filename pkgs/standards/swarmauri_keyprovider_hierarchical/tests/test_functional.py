import pytest

from swarmauri_keyprovider_hierarchical import HierarchicalKeyProvider
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_core.key_providers.types import KeySpec, KeyAlg, KeyClass, ExportPolicy, KeyUse


@pytest.mark.test
@pytest.mark.func
@pytest.mark.asyncio
async def test_jwks_merge() -> None:
    child_a = LocalKeyProvider()
    child_b = LocalKeyProvider()
    provider = HierarchicalKeyProvider({"a": child_a, "b": child_b})
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    await provider.create_key(spec)
    await provider.create_key(spec)
    jwks = await provider.jwks()
    assert len(jwks["keys"]) == 2
