"""Tests for OAuth 2.0 Demonstrating Proof of Possession (DPoP) - RFC 9449.

These tests verify DPoP proof creation and validation per RFC 9449 and ensure
that the helper functions respect the ``enable_rfc9449`` feature flag.
"""

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from auto_authn.v2.rfc9449_dpop import (
    RFC9449_SPEC_URL,
    create_proof,
    verify_proof,
    jwk_from_public_key,
    jwk_thumbprint,
)


@pytest.mark.unit
def test_dpop_proof_verification():
    """DPoP proof must match HTTP method and URL and bind to the access token."""
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    jwk = jwk_from_public_key(public_key)
    jkt = jwk_thumbprint(jwk)
    proof = create_proof(private_pem, "POST", "https://rs.example.com/resource")
    assert (
        verify_proof(proof, "POST", "https://rs.example.com/resource", jkt=jkt) == jkt
    )


@pytest.mark.unit
def test_mismatched_method_rejected():
    """Verification fails when HTTP method does not match proof."""
    private_key = Ed25519PrivateKey.generate()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    proof = create_proof(private_pem, "GET", "https://rs.example.com/data")
    with pytest.raises(ValueError):
        verify_proof(proof, "POST", "https://rs.example.com/data")


@pytest.mark.unit
def test_feature_toggle_disabled():
    """When disabled, proof verification returns empty string."""
    private_key = Ed25519PrivateKey.generate()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    proof = create_proof(
        private_pem, "GET", "https://rs.example.com/data", enabled=False
    )
    assert proof == ""
    assert verify_proof("", "GET", "https://rs.example.com/data", enabled=False) == ""


@pytest.mark.unit
def test_spec_url_constant():
    """Ensure the exported constant points to the RFC 9449 specification."""
    assert RFC9449_SPEC_URL.endswith("rfc9449")
