"""Tests for RFC 8037, RFC 8176 and RFC 8291 compliance.

Each test explicitly references the corresponding RFC to ensure that the
behaviour implemented in :mod:`auto_authn.v2` adheres to the specification
when the feature flag is enabled and raises an error otherwise.
"""

from __future__ import annotations

import base64

import pytest

from auto_authn.v2 import (
    RFC8037_SPEC_URL,
    RFC8176_SPEC_URL,
    RFC8291_SPEC_URL,
    amr_description,
    decrypt_push_message,
    encrypt_push_message,
    parse_okp_jwk,
)
from auto_authn.v2.runtime_cfg import settings


def test_rfc8037_parse_okp_jwk(monkeypatch):
    """RFC 8037: OKP JWK parsing respects feature flag."""
    assert "8037" in RFC8037_SPEC_URL
    monkeypatch.setattr(settings, "enable_rfc8037", True)
    jwk = {
        "kty": "OKP",
        "crv": "Ed25519",
        "x": base64.urlsafe_b64encode(b"foo").decode().rstrip("="),
    }
    key = parse_okp_jwk(jwk)
    assert key.crv == "Ed25519"
    monkeypatch.setattr(settings, "enable_rfc8037", False)
    with pytest.raises(NotImplementedError):
        parse_okp_jwk(jwk)


def test_rfc8176_amr_description(monkeypatch):
    """RFC 8176: AMR code lookup respects feature flag."""
    assert "8176" in RFC8176_SPEC_URL
    monkeypatch.setattr(settings, "enable_rfc8176", True)
    assert amr_description("pwd") == "Password"
    monkeypatch.setattr(settings, "enable_rfc8176", False)
    with pytest.raises(NotImplementedError):
        amr_description("pwd")


def test_rfc8291_message_encryption(monkeypatch):
    """RFC 8291: Message encryption routines respect feature flag."""
    assert "8291" in RFC8291_SPEC_URL
    monkeypatch.setattr(settings, "enable_rfc8291", True)
    msg = "hello"
    cipher = encrypt_push_message(msg)
    assert cipher != msg
    assert decrypt_push_message(cipher) == msg
    monkeypatch.setattr(settings, "enable_rfc8291", False)
    with pytest.raises(NotImplementedError):
        encrypt_push_message(msg)
