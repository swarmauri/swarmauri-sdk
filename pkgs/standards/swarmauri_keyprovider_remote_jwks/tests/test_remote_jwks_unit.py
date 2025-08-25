import json
from unittest.mock import patch

import pytest

from swarmauri_core.keys.types import KeySpec, KeyClass, KeyAlg
from swarmauri_core.crypto.types import KeyUse, ExportPolicy
from swarmauri_keyprovider_remote_jwks import RemoteJwksKeyProvider

SAMPLE_JWKS = {
    "keys": [
        {"kty": "RSA", "kid": "test.1", "n": "0", "e": "AQAB", "alg": "RS256"},
        {
            "kty": "EC",
            "kid": "test.2",
            "crv": "P-256",
            "x": "0",
            "y": "0",
            "alg": "ES256",
        },
    ]
}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_key_and_list_versions() -> None:
    provider = RemoteJwksKeyProvider(jwks_url="https://example.com/jwks")
    with patch.object(
        provider,
        "_fetch_json_conditional",
        return_value=(SAMPLE_JWKS, None, None, False),
    ):
        provider.refresh(force=True)
    ref = await provider.get_key("test", 1)
    assert json.loads(ref.public)["kid"] == "test.1"
    versions = await provider.list_versions("test")
    assert versions == (1, 2)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_local_key_roundtrip() -> None:
    provider = RemoteJwksKeyProvider(jwks_url="https://example.com/jwks")
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    ref = await provider.create_key(spec)
    fetched = await provider.get_key(ref.kid, include_secret=True)
    assert fetched.kid == ref.kid
    with patch.object(
        provider,
        "_fetch_json_conditional",
        return_value=({"keys": []}, None, None, False),
    ):
        jwks = await provider.jwks()
    assert any(k["kid"] == f"{ref.kid}.{ref.version}" for k in jwks["keys"])
