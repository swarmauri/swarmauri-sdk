import time
from unittest.mock import patch

import pytest

from swarmauri_keyprovider_remote_jwks import RemoteJwksKeyProvider

SAMPLE_JWKS = {
    "keys": [{"kty": "RSA", "kid": "test.1", "n": "0", "e": "AQAB", "alg": "RS256"}]
}


@pytest.mark.perf
def test_refresh_performance() -> None:
    provider = RemoteJwksKeyProvider(jwks_url="https://example.com/jwks")
    with patch.object(
        provider,
        "_fetch_json_conditional",
        return_value=(SAMPLE_JWKS, None, None, False),
    ):
        start = time.perf_counter()
        provider.refresh(force=True)
        duration = time.perf_counter() - start
    assert duration < 0.01
