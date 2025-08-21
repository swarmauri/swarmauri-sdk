import pytest

from swarmauri_keyproviders import SshKeyProvider
from swarmauri_core.keys.types import KeySpec, KeyAlg, KeyClass, ExportPolicy, KeyUse


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_rsa_jwk() -> None:
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
    assert jwk["kty"] == "RSA"


@pytest.mark.i9n
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
