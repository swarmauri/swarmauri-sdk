"""Tests for the JSON Web Token (JWT) Profile for OAuth 2.0 Access Tokens (RFC 9068).

RFC 9068 specifies that access tokens using the JWT profile MUST include
standard claims like ``iss`` and ``aud`` and use the JOSE header ``typ`` value
``at+jwt``. These tests verify enforcement of those requirements when the
feature flag is enabled and ensure tokens are accepted when it is disabled.
"""

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from jwt.exceptions import InvalidTokenError

from auto_authn.v2 import runtime_cfg
from auto_authn.v2.jwtoken import JWTCoder


@pytest.mark.unit
def test_rfc9068_claims_enforced(monkeypatch):
    """RFC 9068 requires specific claims and the ``at+jwt`` header."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc9068", True)
    monkeypatch.setattr(runtime_cfg.settings, "jwt_issuer", "https://issuer.example")
    monkeypatch.setattr(runtime_cfg.settings, "jwt_audience", "api")
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
    token = coder.sign(sub="alice", tid="tenant")
    header = jwt.get_unverified_header(token)
    assert header["typ"] == "at+jwt"
    payload = coder.decode(token)
    assert payload["iss"] == "https://issuer.example"
    assert payload["aud"] == "api"
    bad_token = jwt.encode({"sub": "alice"}, private_pem, algorithm="EdDSA")
    with pytest.raises(InvalidTokenError):
        coder.decode(bad_token)


@pytest.mark.unit
def test_rfc9068_feature_toggle(monkeypatch):
    """When disabled, tokens need not follow RFC 9068."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc9068", False)
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
    header = jwt.get_unverified_header(token)
    assert header["typ"] == "JWT"
    payload = coder.decode(token)
    assert "iss" not in payload
    assert "aud" not in payload
