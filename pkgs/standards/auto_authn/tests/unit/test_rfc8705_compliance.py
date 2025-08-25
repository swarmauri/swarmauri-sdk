"""Tests for OAuth 2.0 Mutual-TLS client authentication (RFC 8705).

RFC 8705 §3.1 states that access tokens bound to a client certificate MUST
contain a ``cnf`` claim with an ``x5t#S256`` member matching the certificate's
SHA-256 thumbprint. The tests below verify that behavior is enforced when the
feature flag is enabled and bypassed when disabled.
"""

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from jwt.exceptions import InvalidTokenError

from auto_authn.v2 import runtime_cfg
from auto_authn.v2.jwtoken import JWTCoder


@pytest.mark.unit
def test_certificate_thumbprint_enforced(monkeypatch):
    """RFC 8705 §3.1 requires matching cnf.x5t#S256 when enabled."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc8705", True)
    private_key_obj = Ed25519PrivateKey.generate()
    public_key_obj = private_key_obj.public_key()

    private_pem = private_key_obj.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = public_key_obj.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    coder = JWTCoder(private_pem, public_pem)
    token = coder.sign(sub="alice", tid="tenant", cert_thumbprint="thumb")
    payload = coder.decode(token, cert_thumbprint="thumb")
    assert payload["cnf"]["x5t#S256"] == "thumb"
    with pytest.raises(InvalidTokenError):
        coder.decode(token, cert_thumbprint="other")


@pytest.mark.unit
def test_feature_toggle_disabled(monkeypatch):
    """When disabled, tokens need not include the cnf claim."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc8705", False)
    private_key_obj = Ed25519PrivateKey.generate()
    public_key_obj = private_key_obj.public_key()

    private_pem = private_key_obj.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = public_key_obj.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    coder = JWTCoder(private_pem, public_pem)
    token = coder.sign(sub="bob", tid="tenant")
    payload = coder.decode(token)
    assert "cnf" not in payload
