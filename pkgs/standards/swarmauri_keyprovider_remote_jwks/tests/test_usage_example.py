import pytest
from unittest.mock import patch
from swarmauri_keyprovider_remote_jwks import RemoteJwksKeyProvider

SAMPLE_JWKS = {
    "keys": [{"kty": "RSA", "kid": "test.1", "n": "0", "e": "AQAB", "alg": "RS256"}]
}


@pytest.mark.example
@pytest.mark.asyncio
async def test_readme_usage_example() -> None:
    provider = RemoteJwksKeyProvider(
        jwks_url="https://example.com/.well-known/jwks.json"
    )
    with patch.object(
        provider,
        "_fetch_json_conditional",
        return_value=(SAMPLE_JWKS, None, None, False),
    ):
        provider.refresh(force=True)
    jwk = await provider.get_public_jwk("test", version=1)
    assert jwk["kid"] == "test.1"
