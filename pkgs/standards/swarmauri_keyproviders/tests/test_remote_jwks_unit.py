import json
from unittest.mock import patch

import pytest

from swarmauri_keyproviders import RemoteJwksKeyProvider

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
