"""Tests for OAuth 2.0 Token Introspection (RFC 7662)."""

import pytest

from tigrbl_auth import rfc7662
from tigrbl_auth.runtime_cfg import settings

RFC_7662 = "RFC 7662"


def setup_function() -> None:
    rfc7662.reset_tokens()


def test_introspect_active_token(monkeypatch):
    """RFC 7662 requires active tokens to return claims including active=True."""
    monkeypatch.setattr(settings, "enable_rfc7662", True)
    rfc7662.register_token("tok123", {"sub": "alice"})
    result = rfc7662.introspect_token("tok123")
    assert result["active"] is True
    assert result["sub"] == "alice"


def test_introspect_inactive_token(monkeypatch):
    """RFC 7662 mandates inactive tokens return only active=False."""
    monkeypatch.setattr(settings, "enable_rfc7662", True)
    result = rfc7662.introspect_token("missing")
    assert result == {"active": False}


def test_introspection_disabled(monkeypatch):
    """The feature can be toggled off via settings.enable_rfc7662."""
    monkeypatch.setattr(settings, "enable_rfc7662", False)
    with pytest.raises(RuntimeError):
        rfc7662.introspect_token("tok123")
