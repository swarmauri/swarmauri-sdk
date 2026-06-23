from __future__ import annotations

import pytest

from swarmauri_transport_https_unicast import HttpsSecurityPolicy, HttpsUnicastTransport


@pytest.mark.example
def test_readme_imports_are_available() -> None:
    transport = HttpsUnicastTransport(
        security_policy=HttpsSecurityPolicy(bearer_token="token")
    )

    assert transport.security_policy.bearer_token == "token"
