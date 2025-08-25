"""Tests for RFC 7517: JSON Web Key (JWK)."""

from auto_authn.v2 import load_signing_jwk, load_public_jwk


def test_jwk_contains_required_fields() -> None:
    priv = load_signing_jwk()
    pub = load_public_jwk()
    assert priv["kty"] == "OKP"
    assert pub["kty"] == "OKP"
