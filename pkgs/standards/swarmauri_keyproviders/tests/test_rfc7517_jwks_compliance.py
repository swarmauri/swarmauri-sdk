from unittest.mock import patch

import pytest

from swarmauri_keyproviders import RemoteJwksKeyProvider

SAMPLE_JWKS = {
    "keys": [{"kty": "RSA", "kid": "test.1", "n": "0", "e": "AQAB", "alg": "RS256"}]
}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_rfc7517_compliant() -> None:
    provider = RemoteJwksKeyProvider(jwks_url="https://example.com/jwks")
    with patch.object(
        provider,
        "_fetch_json_conditional",
        return_value=(SAMPLE_JWKS, None, None, False),
    ):
        provider.refresh(force=True)
    jwks = await provider.jwks()
    assert "keys" in jwks and jwks["keys"][0]["kty"] == "RSA"
