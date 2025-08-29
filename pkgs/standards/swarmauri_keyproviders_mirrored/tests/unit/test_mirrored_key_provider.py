import pytest

from swarmauri_core.keys.types import ExportPolicy, KeyAlg, KeyClass, KeySpec
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_keyproviders_mirrored import MirroredKeyProvider


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_key_mirrors_to_secondary() -> None:
    primary = LocalKeyProvider()
    secondary = LocalKeyProvider()
    provider = MirroredKeyProvider(primary, secondary, mirror_mode="full")
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        size_bits=None,
        label="test",
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        uses=(),
    )
    pref = await provider.create_key(spec)
    shadow = provider._get_shadow(pref.kid, pref.version)
    assert shadow is not None
    sec_ref = await secondary.get_key(shadow.sec_kid, shadow.sec_version)
    assert sec_ref.public is pref.public
