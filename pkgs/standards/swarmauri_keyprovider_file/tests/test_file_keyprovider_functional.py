import pytest

from swarmauri_keyprovider_file import FileKeyProvider
from swarmauri_core.keys.types import KeySpec, KeyClass, KeyAlg, ExportPolicy
from swarmauri_core.crypto.types import KeyUse


@pytest.mark.asyncio
@pytest.mark.test
@pytest.mark.i9n
async def test_rotate_and_jwks(tmp_path):
    provider = FileKeyProvider(tmp_path)
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    ref = await provider.create_key(spec)
    await provider.rotate_key(ref.kid)
    jwks = await provider.jwks()
    assert any(k["kid"].startswith(ref.kid) for k in jwks["keys"])
