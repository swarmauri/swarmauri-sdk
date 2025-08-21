import pytest

from swarmauri_keyprovider_hierarchical import HierarchicalKeyProvider, CreateRule
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_core.keys.types import (
    KeySpec,
    KeyAlg,
    KeyClass,
    ExportPolicy,
    KeyUse,
)


@pytest.mark.test
@pytest.mark.unit
@pytest.mark.asyncio
async def test_policy_routing() -> None:
    child_a = LocalKeyProvider()
    child_b = LocalKeyProvider()
    provider = HierarchicalKeyProvider(
        {"a": child_a, "b": child_b},
        create_policy=[CreateRule(provider="b", klass=KeyClass.symmetric)],
    )
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    ref = await provider.create_key(spec)
    assert ref.kid in child_b._store
