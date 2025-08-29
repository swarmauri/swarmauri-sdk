from unittest.mock import patch

import pytest

from swarmauri_keyprovider_remote_jwks import RemoteJwksKeyProvider

SAMPLE_JWKS = {
    "keys": [{"kty": "RSA", "kid": "test.1", "n": "0", "e": "AQAB", "alg": "RS256"}]
}


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_refresh_uses_cache() -> None:
    provider = RemoteJwksKeyProvider(jwks_url="https://example.com/jwks")
    side_effect = [
        (SAMPLE_JWKS, "E", "L", False),
        ({}, "E", "L", True),
    ]
    with patch.object(provider, "_fetch_json_conditional", side_effect=side_effect):
        provider.refresh(force=True)
        provider.refresh(force=True)
    jwk = await provider.get_public_jwk("test", 1)
    assert jwk["kid"] == "test.1"
