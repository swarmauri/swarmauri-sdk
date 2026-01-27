import pytest

from swarmauri_core.key_providers.types import ExportPolicy, KeyAlg, KeyClass, KeySpec
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_keyproviders_mirrored import MirroredKeyProvider


@pytest.mark.unit
@pytest.mark.asyncio
async def test_jwks_conforms_rfc7517() -> None:
    primary = LocalKeyProvider()
    secondary = LocalKeyProvider()
    provider = MirroredKeyProvider(primary, secondary)
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        size_bits=None,
        label="rfc",
        export_policy=ExportPolicy.PUBLIC_ONLY,
        uses=(),
    )
    await provider.create_key(spec)
    jwks = await provider.jwks()
    assert "keys" in jwks
    assert all("kid" in jwk for jwk in jwks["keys"])
