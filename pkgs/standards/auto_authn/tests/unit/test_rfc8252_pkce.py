"""Tests for OAuth 2.0 for Native Apps (RFC 8252) PKCE requirements.

RFC excerpt (RFC 8252 §7.3 and RFC 7636 §4.1):

Native apps MUST use the Proof Key for Code Exchange (PKCE [RFC7636])
extension to OAuth 2.0 when using the authorization code grant.

The code_verifier MUST be a high-entropy cryptographic random string using the
unreserved characters [A-Z] / [a-z] / [0-9] / "-" / "." / "_" / "~",
with a minimum length of 43 characters and a maximum length of 128 characters.
"""

import pytest

from auto_authn.v2 import (
    create_code_challenge,
    create_code_verifier,
    verify_code_challenge,
)


@pytest.mark.unit
def test_code_verifier_meets_rfc7636_requirements():
    """Generated verifier satisfies RFC 7636 §4.1."""

    verifier = create_code_verifier()
    assert 43 <= len(verifier) <= 128
    allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"
    assert all(ch in allowed for ch in verifier)


@pytest.mark.unit
def test_code_challenge_s256_matches_known_example():
    """RFC 7636 Appendix B example."""

    verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
    expected = "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"
    assert create_code_challenge(verifier) == expected


@pytest.mark.unit
def test_verify_code_challenge_round_trip():
    """Challenge derived from verifier validates correctly."""

    verifier = create_code_verifier(60)
    challenge = create_code_challenge(verifier)
    assert verify_code_challenge(verifier, challenge)


@pytest.mark.unit
def test_invalid_verifier_rejected():
    """Invalid verifier raises ValueError."""

    with pytest.raises(ValueError):
        create_code_challenge("short")
