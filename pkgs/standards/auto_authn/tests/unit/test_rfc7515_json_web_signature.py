"""Tests for JSON Web Signature (RFC 7515).

RFC 7515 §4.1 requires that the JOSE header include an ``alg`` parameter and
forbids the unsecured ``none`` algorithm. These tests ensure the auto_authn
package enforces that requirement when the feature flag is enabled.
"""

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from jwt.exceptions import InvalidTokenError

from auto_authn.v2 import runtime_cfg
from auto_authn.v2.jwtoken import JWTCoder
from auto_authn.v2.rfc7515 import RFC7515_SPEC_URL


@pytest.mark.unit
def test_jws_alg_header_enforced(monkeypatch):
    """RFC 7515 §4.1 forbids using the ``none`` algorithm when enabled."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc7515", True)
    priv = ed25519.Ed25519PrivateKey.generate()
    pub = priv.public_key()
    private_pem = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    coder = JWTCoder(private_pem, public_pem)
    token = coder.sign(sub="alice", tid="tenant")
    assert coder.decode(token)["sub"] == "alice"

    bad = jwt.encode({"sub": "alice"}, key="", algorithm="none")
    with pytest.raises(InvalidTokenError, match="RFC 7515"):
        coder.decode(bad)


@pytest.mark.unit
def test_feature_toggle_skips_header_validation(monkeypatch):
    """When disabled, RFC 7515 validation is not applied."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc7515", False)
    priv = ed25519.Ed25519PrivateKey.generate()
    pub = priv.public_key()
    private_pem = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    coder = JWTCoder(private_pem, public_pem)
    bad = jwt.encode({"sub": "alice"}, key="", algorithm="none")
    with pytest.raises(InvalidTokenError) as exc:
        coder.decode(bad)
    assert "RFC 7515" not in str(exc.value)


def test_spec_url_constant():
    """Ensure the module exposes the official RFC 7515 specification URL."""
    assert RFC7515_SPEC_URL.endswith("rfc7515")
