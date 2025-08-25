"""Tests for Proof-of-Possession Key Semantics for JWTs (RFC 7800)."""

import pytest

from auto_authn.v2 import runtime_cfg
from auto_authn.v2.rfc7638 import jwk_thumbprint
from auto_authn.v2.rfc7800 import validate_cnf_claim


@pytest.mark.unit
def test_validate_cnf(monkeypatch):
    """A matching ``cnf`` claim validates against the supplied JWK."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc7800", True)
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
    }
    jkt = jwk_thumbprint(jwk)
    payload = {"sub": "alice", "cnf": {"jkt": jkt}}
    assert validate_cnf_claim(payload, jwk)
    payload["cnf"]["jkt"] = "other"
    assert not validate_cnf_claim(payload, jwk)


@pytest.mark.unit
def test_disabled(monkeypatch):
    """When disabled mismatched thumbprints are ignored."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc7800", False)
    assert validate_cnf_claim({}, {}) is True
