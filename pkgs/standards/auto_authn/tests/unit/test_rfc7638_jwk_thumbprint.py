"""Tests for JSON Web Key Thumbprint (RFC 7638).

The tests validate that :func:`auto_authn.rfc7638.jwk_thumbprint`
produces the expected base64url value from the RFC 7638 example and that
:func:`auto_authn.rfc7638.verify_jwk_thumbprint` respects the runtime
feature toggle.
"""

import base64
import hashlib
import json

import pytest

from auto_authn.rfc7638 import jwk_thumbprint, verify_jwk_thumbprint

EXAMPLE_JWK = {
    "kty": "RSA",
    "n": "0vx7agoebGcQSuuPiLJXZptN9nndrQmbXEps2aiAFbWhM78LhWx4cbbfAAtVT86zwu1RK7aPFFxuhDR1L6tSoc_BJECPebWKRXjBZCiFV4n3oknjhMstn64tZ_2W-5JsGY4Hc5n9yBXArwl93lqt7_RN5w6Cf0h4QyQ5v-65YGjQR0_FDW2QvzqY368QQMicAtaSqzs8KJZgnYb9c7d0zgdAZHzu6qMQvRL5hajrn1n91CbOpbISD08qNLyrdkt-bFTWhAI4vMQFh6WeZu0fM4lFd2NcRwr3XPksINHaQ-G_xBniIqbw0Ls1jF44-csFCur-kEgU8awapJzKnqDKgw",
    "e": "AQAB",
    "alg": "RS256",
    "kid": "2011-04-29",
}


@pytest.mark.unit
def test_thumbprint_matches_rfc_example():
    """Computes the known thumbprint from RFC 7638 §3.1."""
    # Manual computation following RFC 7638 to cross-check helper
    obj = {"e": EXAMPLE_JWK["e"], "kty": EXAMPLE_JWK["kty"], "n": EXAMPLE_JWK["n"]}
    canonical = json.dumps(obj, separators=(",", ":"), sort_keys=True).encode()
    expected = (
        base64.urlsafe_b64encode(hashlib.sha256(canonical).digest())
        .decode()
        .rstrip("=")
    )
    assert jwk_thumbprint(EXAMPLE_JWK) == expected
    assert expected == "NzbLsXh8uDCcd-6MNwXF4W_7noWXFZAfHkxZsRGC9Xs"


@pytest.mark.unit
def test_verification_respects_feature_flag(monkeypatch):
    """Verification honours the global RFC 7638 enable flag."""
    thumb = jwk_thumbprint(EXAMPLE_JWK)
    assert verify_jwk_thumbprint(EXAMPLE_JWK, thumb, enabled=True)
    assert verify_jwk_thumbprint(EXAMPLE_JWK, "bad", enabled=False)
    assert not verify_jwk_thumbprint(EXAMPLE_JWK, "bad", enabled=True)
