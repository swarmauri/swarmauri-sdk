import pytest

from swarmauri_keyprovider_ssh import SshKeyProvider
from swarmauri_core.keys.types import KeySpec, KeyAlg, KeyClass, ExportPolicy, KeyUse


@pytest.mark.asyncio
async def test_jwks_contains_key() -> None:
    kp = SshKeyProvider()
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ECDSA_P256_SHA256,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.PUBLIC_ONLY,
    )
    ref = await kp.create_key(spec)
    jwks = await kp.jwks()
    assert any(key["kid"].startswith(ref.kid) for key in jwks["keys"])
