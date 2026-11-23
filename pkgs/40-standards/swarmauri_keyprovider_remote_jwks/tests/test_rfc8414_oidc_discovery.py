from unittest.mock import patch

import pytest

from swarmauri_keyprovider_remote_jwks import RemoteJwksKeyProvider

OPENID_CONFIG = {"jwks_uri": "https://example.com/jwks"}


@pytest.mark.unit
def test_rfc8414_discovery() -> None:
    provider = RemoteJwksKeyProvider(issuer="https://issuer.example")
    with patch.object(
        provider,
        "_fetch_json_conditional",
        return_value=(OPENID_CONFIG, None, None, False),
    ):
        url = provider._resolve_jwks_uri("https://issuer.example")
    assert url == "https://example.com/jwks"
