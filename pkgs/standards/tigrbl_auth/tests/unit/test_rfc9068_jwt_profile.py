"""Tests for JWT Profile for OAuth 2.0 Access Tokens (RFC 9068).

RFC 9068 defines a profile for issuing OAuth 2.0 access tokens as JWTs.
The tests verify that when the feature is enabled the mandatory ``iss`` and
``aud`` claims are required and validated, and that the behaviour is bypassed
when the feature flag is disabled.
"""

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from tigrbl_auth import runtime_cfg
from tigrbl_auth.errors import InvalidTokenError
from tigrbl_auth.jwtoken import JWTCoder
from tigrbl_auth.rfc.rfc9068 import add_rfc9068_claims, validate_rfc9068_claims


@pytest.mark.unit
def test_helpers_apply_and_validate():
    """RFC 9068 claim helpers add and validate ``iss`` and ``aud``."""
    payload = {"sub": "alice", "exp": 1}
    augmented = add_rfc9068_claims(payload, issuer="issuer", audience=["api"])
    assert augmented["iss"] == "issuer"
    assert augmented["aud"] == ["api"]
    validate_rfc9068_claims(augmented, issuer="issuer", audience=["api"])
    with pytest.raises(InvalidTokenError):
        validate_rfc9068_claims(augmented, issuer="other", audience=["api"])


@pytest.mark.unit
def test_jwtoken_enforces_claims(monkeypatch):
    """JWTCoder integrates RFC 9068 when the feature is enabled."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc9068", True)
    private_key_obj = ed25519.Ed25519PrivateKey.generate()
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
    token = coder.sign(
        sub="alice",
        tid="tenant",
        issuer="https://issuer.example.com",
        audience="api",
    )
    payload = coder.decode(
        token,
        issuer="https://issuer.example.com",
        audience="api",
    )
    assert payload["iss"] == "https://issuer.example.com"
    assert payload["aud"] == "api"
    with pytest.raises(InvalidTokenError):
        coder.decode(token, issuer="https://issuer.example.com", audience="other")


@pytest.mark.unit
def test_feature_toggle_disabled(monkeypatch):
    """When disabled, ``iss`` and ``aud`` are neither required nor added."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc9068", False)
    private_key_obj = ed25519.Ed25519PrivateKey.generate()
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
    assert "iss" not in payload
    assert "aud" not in payload
