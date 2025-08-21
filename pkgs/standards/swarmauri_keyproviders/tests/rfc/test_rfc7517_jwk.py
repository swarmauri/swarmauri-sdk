import pytest

from swarmauri_keyproviders import SshKeyProvider
from swarmauri_core.keys.types import KeySpec, KeyAlg, KeyClass, ExportPolicy, KeyUse


@pytest.mark.rfc
@pytest.mark.asyncio
async def test_jwk_structure_matches_rfc7517() -> None:
    kp = SshKeyProvider()
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.RSA_PSS_SHA256,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.PUBLIC_ONLY,
        size_bits=3072,
    )
    ref = await kp.create_key(spec)
    jwk = await kp.get_public_jwk(ref.kid)
    assert {"kty", "n", "e", "kid"}.issubset(jwk.keys())
