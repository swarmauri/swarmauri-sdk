"""Tests for RFC 7517: JSON Web Key (JWK)."""

import pytest

from auto_authn.v2 import runtime_cfg
from auto_authn.v2 import load_signing_jwk, load_public_jwk


def test_jwk_contains_required_fields() -> None:
    priv = load_signing_jwk()
    pub = load_public_jwk()
    assert priv.kty == "OKP"
    assert pub.kty == "OKP"


def test_feature_flag(monkeypatch) -> None:
    """Disabling RFC 7517 raises errors when loading keys."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc7517", False)
    with pytest.raises(RuntimeError):
        load_signing_jwk()
    with pytest.raises(RuntimeError):
        load_public_jwk()
