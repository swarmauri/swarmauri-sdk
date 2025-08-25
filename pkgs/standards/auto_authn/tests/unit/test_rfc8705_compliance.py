"""Tests for OAuth 2.0 Mutual-TLS client authentication (RFC 8705).

RFC 8705 §3.1 states that access tokens bound to a client certificate MUST
contain a ``cnf`` claim with an ``x5t#S256`` member matching the certificate's
SHA-256 thumbprint. See https://www.rfc-editor.org/rfc/rfc8705 for details.
The tests below verify that behavior is enforced when the feature flag is
enabled and bypassed when disabled.
"""

from datetime import UTC, datetime, timedelta

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from auto_authn.v2.exceptions import InvalidTokenError

import auto_authn.v2.runtime_cfg as runtime_cfg
from auto_authn.v2.jwtoken import JWTCoder
from auto_authn.v2.rfc8705 import (
    RFC8705_SPEC_URL,
    thumbprint_from_cert_pem,
    validate_certificate_binding,
)


def _generate_cert_pem() -> bytes:
    """Return a minimal self-signed certificate in PEM format."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name(
        [x509.NameAttribute(NameOID.COMMON_NAME, "example.com")]
    )
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(UTC))
        .not_valid_after(datetime.now(UTC) + timedelta(days=1))
        .sign(key, hashes.SHA256())
    )
    return cert.public_bytes(serialization.Encoding.PEM)


@pytest.mark.unit
def test_thumbprint_and_binding_helpers():
    """RFC 8705 §3.1 thumbprint derivation and binding validation."""
    cert_pem = _generate_cert_pem()
    thumbprint = thumbprint_from_cert_pem(cert_pem)
    payload = {"cnf": {"x5t#S256": thumbprint}}
    validate_certificate_binding(payload, thumbprint, enabled=True)  # should not raise
    with pytest.raises(InvalidTokenError):
        validate_certificate_binding(payload, "mismatch", enabled=True)


@pytest.mark.unit
def test_certificate_thumbprint_enforced(monkeypatch):
    """RFC 8705 §3.1 requires matching cnf.x5t#S256 when enabled."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc8705", True)
    coder = JWTCoder.default()
    token = coder.sign(sub="alice", tid="tenant", cert_thumbprint="thumb")
    payload = coder.decode(token, cert_thumbprint="thumb")
    assert payload["cnf"]["x5t#S256"] == "thumb"
    with pytest.raises(InvalidTokenError):
        coder.decode(token, cert_thumbprint="other")


@pytest.mark.unit
def test_sign_requires_thumbprint_when_enabled(monkeypatch):
    """RFC 8705 demands certificate binding when feature flag is on."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc8705", True)
    coder = JWTCoder.default()
    with pytest.raises(ValueError):
        coder.sign(sub="carol", tid="tenant")


@pytest.mark.unit
def test_feature_toggle_disabled(monkeypatch):
    """When disabled, tokens need not include the cnf claim."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc8705", False)
    coder = JWTCoder.default()
    token = coder.sign(sub="bob", tid="tenant")
    payload = coder.decode(token)
    assert "cnf" not in payload


@pytest.mark.unit
def test_decode_requires_cnf_claim_when_enabled(monkeypatch):
    """RFC 8705 §3.1 rejects tokens lacking cnf when feature flag is enabled."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc8705", False)
    coder = JWTCoder.default()
    token = coder.sign(sub="dave", tid="tenant")
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc8705", True)
    with pytest.raises(InvalidTokenError):
        coder.decode(token, cert_thumbprint="thumb")


@pytest.mark.unit
def test_spec_url_constant():
    """Ensure the exported constant points to the RFC 8705 specification."""
    assert RFC8705_SPEC_URL.endswith("rfc8705")


@pytest.mark.unit
def test_validate_binding_respects_enabled_flag():
    """``validate_certificate_binding`` bypasses checks when disabled."""
    payload = {"cnf": {"x5t#S256": "thumb"}}
    validate_certificate_binding(payload, "other", enabled=False)
