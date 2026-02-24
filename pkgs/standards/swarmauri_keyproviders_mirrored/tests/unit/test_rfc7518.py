import pytest

from swarmauri_core.key_providers.types import KeyAlg
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_keyproviders_mirrored import MirroredKeyProvider


@pytest.mark.unit
@pytest.mark.asyncio
async def test_supported_algs_rfc7518() -> None:
    primary = LocalKeyProvider()
    secondary = LocalKeyProvider()
    provider = MirroredKeyProvider(primary, secondary)
    supports = provider.supports()
    assert KeyAlg.ED25519.value in supports["algs"]
