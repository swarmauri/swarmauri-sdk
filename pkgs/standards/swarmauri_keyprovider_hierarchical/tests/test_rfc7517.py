import pytest

from swarmauri_keyprovider_hierarchical import HierarchicalKeyProvider
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_core.keys.types import KeySpec, KeyAlg, KeyClass, ExportPolicy, KeyUse


@pytest.mark.test
@pytest.mark.rfc
@pytest.mark.asyncio
async def test_jwks_structure() -> None:
    child = LocalKeyProvider()
    provider = HierarchicalKeyProvider({"a": child})
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    await provider.create_key(spec)
    jwks = await provider.jwks()
    assert "keys" in jwks and isinstance(jwks["keys"], list)
    assert all("kid" in jwk and "kty" in jwk for jwk in jwks["keys"])
