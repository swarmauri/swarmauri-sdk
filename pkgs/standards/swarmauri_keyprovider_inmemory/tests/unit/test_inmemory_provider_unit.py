import pytest
from swarmauri_keyprovider_inmemory import InMemoryKeyProvider
from swarmauri_core.key_providers.types import KeySpec, KeyClass, KeyAlg, ExportPolicy, KeyUse


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_and_get() -> None:
    provider = InMemoryKeyProvider()
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    ref = await provider.create_key(spec)
    fetched = await provider.get_key(ref.kid)
    assert fetched.kid == ref.kid
    assert fetched.material == ref.material


@pytest.mark.unit
def test_type() -> None:
    assert InMemoryKeyProvider().type == "InMemoryKeyProvider"
