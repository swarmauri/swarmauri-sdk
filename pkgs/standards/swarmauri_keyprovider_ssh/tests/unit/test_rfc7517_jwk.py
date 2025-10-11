import pytest

from swarmauri_keyprovider_ssh import SshKeyProvider
from swarmauri_core.key_providers.types import KeySpec, KeyAlg, KeyClass, ExportPolicy, KeyUse


@pytest.mark.unit
@pytest.mark.asyncio
async def test_rfc7517_ed25519_jwk() -> None:
    kp = SshKeyProvider()
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.PUBLIC_ONLY,
    )
    ref = await kp.create_key(spec)
    jwk = await kp.get_public_jwk(ref.kid)
    assert jwk["kty"] == "OKP"
    assert jwk["crv"] == "Ed25519"
    assert "x" in jwk
    assert jwk["kid"] == f"{ref.kid}.{ref.version}"
