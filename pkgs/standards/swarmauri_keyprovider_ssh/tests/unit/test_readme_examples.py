import pytest

from swarmauri_keyprovider_ssh import SshKeyProvider
from swarmauri_core.key_providers.types import (
    KeySpec,
    KeyAlg,
    KeyClass,
    ExportPolicy,
    KeyUse,
)


@pytest.mark.example
@pytest.mark.asyncio
async def test_create_ed25519_key_and_export_jwk() -> None:
    provider = SshKeyProvider()
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.PUBLIC_ONLY,
    )
    ref = await provider.create_key(spec)
    jwk = await provider.get_public_jwk(ref.kid)
    assert jwk["kty"] == "OKP"
    assert jwk["crv"] == "Ed25519"


@pytest.mark.example
@pytest.mark.asyncio
async def test_rotate_key_tracks_versions() -> None:
    provider = SshKeyProvider()
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
    )
    ref = await provider.create_key(spec)
    await provider.rotate_key(ref.kid)
    versions = await provider.list_versions(ref.kid)
    assert versions == (1, 2)
