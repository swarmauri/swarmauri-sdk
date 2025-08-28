"""Tests for EdDSA helpers (RFC 8037).

These tests exercise the minimal Ed25519 signing utilities and feature
flag behaviour defined in :mod:`auto_authn.rfc8037`.
"""

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from auto_authn.rfc8037 import (
    RFC8037_SPEC_URL,
    sign_eddsa,
    verify_eddsa,
)
from auto_authn.runtime_cfg import settings


@pytest.mark.unit
def test_sign_verify_round_trip():
    """Signature generation and verification succeed when enabled."""
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    message = b"payload"
    sig = sign_eddsa(message, priv, enabled=True)
    assert sig != message
    assert verify_eddsa(message, sig, pub, enabled=True)


@pytest.mark.unit
def test_sign_verify_disabled():
    """When disabled, signing returns the message and verification passes."""
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    message = b"payload"
    sig = sign_eddsa(message, priv, enabled=False)
    assert sig == message
    assert verify_eddsa(message, sig, pub, enabled=False)


@pytest.mark.unit
def test_respects_runtime_setting(monkeypatch):
    """Default behaviour follows :mod:`runtime_cfg` toggle."""
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    message = b"payload"
    monkeypatch.setattr(settings, "enable_rfc8037", False)
    assert sign_eddsa(message, priv) == message
    assert verify_eddsa(message, message, pub)
    monkeypatch.setattr(settings, "enable_rfc8037", True)
    sig = sign_eddsa(message, priv)
    assert sig != message
    assert verify_eddsa(message, sig, pub)


@pytest.mark.unit
def test_spec_url_constant():
    """Spec URL constant references the official RFC document."""
    assert RFC8037_SPEC_URL.endswith("rfc8037")
