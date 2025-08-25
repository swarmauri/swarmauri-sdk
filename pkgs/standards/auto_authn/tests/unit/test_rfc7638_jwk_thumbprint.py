"""Tests for JSON Web Key (JWK) Thumbprint (RFC 7638)."""

import pytest

from auto_authn.v2 import runtime_cfg
from auto_authn.v2.rfc7638 import jwk_thumbprint


@pytest.mark.unit
def test_thumbprint_example(monkeypatch):
    """The example JWK thumbprint from RFC 7638 is produced."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc7638", True)
    jwk = {
        "kty": "RSA",
        "n": (
            "0vx7agoebGcQSuuPiLJXZptN9nndrQmbXEps2aiAFbWhM78LhWx4cbbfAAt"
            "VT86zwu1RK7aPFFxuhDR1L6tSoc_BJECPebWKRXjBZCiFV4n3oknjhMstn6"
            "4tZ_2W-5JsGY4Hc5n9yBXArwl93lqt7_RN5w6Cf0h4QyQ5v-65YGjQR0_FD"
            "W2QvzqY368QQMicAtaSqzs8KJZgnYb9c7d0zgdAZHzu6qMQvRL5hajrn1n9"
            "1CbOpbISD08qNLyrdkt-bFTWhAI4vMQFh6WeZu0fM4lFd2NcRwr3XPksINH"
            "aQ-G_xBniIqbw0Ls1jF44-csFCur-kEgU8awapJzKnqDKgw"
        ),
        "e": "AQAB",
        "alg": "RS256",
        "kid": "2011-04-29",
    }
    thumbprint = jwk_thumbprint(jwk)
    assert thumbprint == "NzbLsXh8uDCcd-6MNwXF4W_7noWXFZAfHkxZsRGC9Xs"


@pytest.mark.unit
def test_disabled(monkeypatch):
    """When the feature is disabled a RuntimeError is raised."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc7638", False)
    with pytest.raises(RuntimeError):
        jwk_thumbprint({"kty": "RSA", "n": "", "e": ""})
