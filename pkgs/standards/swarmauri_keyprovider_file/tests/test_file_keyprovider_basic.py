import pytest

from swarmauri_keyprovider_file import FileKeyProvider
from swarmauri_core.keys.types import KeySpec, KeyClass, KeyAlg, ExportPolicy
from swarmauri_core.crypto.types import KeyUse


@pytest.mark.asyncio
@pytest.mark.test
@pytest.mark.unit
async def test_create_and_get(tmp_path):
    provider = FileKeyProvider(tmp_path)
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    ref = await provider.create_key(spec)
    fetched = await provider.get_key(ref.kid, include_secret=True)
    assert fetched.material is not None
    assert fetched.kid == ref.kid
