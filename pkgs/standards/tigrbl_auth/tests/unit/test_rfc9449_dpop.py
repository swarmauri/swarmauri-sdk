"""Tests for OAuth 2.0 Demonstrating Proof of Possession (DPoP) - RFC 9449.

These tests verify DPoP proof creation and validation per RFC 9449 and ensure
that the helper functions respect the ``enable_rfc9449`` feature flag.
"""

import asyncio
import pytest

from tigrbl_auth.deps import (
    ExportPolicy,
    KeyAlg,
    KeyClass,
    KeySpec,
    KeyUse,
    LocalKeyProvider,
)
from tigrbl_auth.rfc.rfc9449_dpop import (
    RFC9449_SPEC_URL,
    create_proof,
    jwk_from_public_key,
    jwk_thumbprint,
    verify_proof,
)


@pytest.mark.unit
def test_dpop_proof_verification():
    """DPoP proof must match HTTP method and URL and bind to the access token."""
    provider = LocalKeyProvider()
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    key = asyncio.run(provider.create_key(spec))
    private_pem = key.material or b""
    jwk = jwk_from_public_key(key.public)
    jkt = jwk_thumbprint(jwk)
    proof = create_proof(private_pem, "POST", "https://rs.example.com/resource")
    assert (
        verify_proof(proof, "POST", "https://rs.example.com/resource", jkt=jkt) == jkt
    )


@pytest.mark.unit
def test_mismatched_method_rejected():
    """Verification fails when HTTP method does not match proof."""
    provider = LocalKeyProvider()
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    key = asyncio.run(provider.create_key(spec))
    private_pem = key.material or b""
    proof = create_proof(private_pem, "GET", "https://rs.example.com/data")
    with pytest.raises(ValueError):
        verify_proof(proof, "POST", "https://rs.example.com/data")


@pytest.mark.unit
def test_feature_toggle_disabled():
    """When disabled, proof verification returns empty string."""
    provider = LocalKeyProvider()
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    key = asyncio.run(provider.create_key(spec))
    private_pem = key.material or b""
    proof = create_proof(
        private_pem, "GET", "https://rs.example.com/data", enabled=False
    )
    assert proof == ""
    assert verify_proof("", "GET", "https://rs.example.com/data", enabled=False) == ""


@pytest.mark.unit
def test_spec_url_constant():
    """Ensure the exported constant points to the RFC 9449 specification."""
    assert RFC9449_SPEC_URL.endswith("rfc9449")
