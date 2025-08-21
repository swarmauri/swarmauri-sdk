"""Tests for RFC 7517 JWK compliance."""

import pytest

from swarmauri_keyprovider_file import FileKeyProvider
from swarmauri_core.keys.types import KeySpec, KeyClass, KeyAlg, ExportPolicy
from swarmauri_core.crypto.types import KeyUse


@pytest.mark.asyncio
@pytest.mark.test
@pytest.mark.unit
async def test_jwk_fields(tmp_path):
    provider = FileKeyProvider(tmp_path)
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.VERIFY,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
    )
    ref = await provider.create_key(spec)
    jwk = await provider.get_public_jwk(ref.kid)
    assert jwk["kty"]
    assert jwk["kid"] == f"{ref.kid}.{ref.version}"
