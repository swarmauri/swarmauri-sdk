"""Tests for WebAuthn algorithm registrations (RFC 8812)."""

import pytest

from auto_authn.v2 import runtime_cfg
from auto_authn.v2.rfc8812 import is_supported_cose_alg


@pytest.mark.unit
def test_algorithm_membership(monkeypatch):
    """Known algorithm identifiers are recognised when enabled."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc8812", True)
    assert is_supported_cose_alg(-257)
    assert not is_supported_cose_alg(-999)


@pytest.mark.unit
def test_disabled(monkeypatch):
    """When disabled no algorithms are treated as supported."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc8812", False)
    assert not is_supported_cose_alg(-257)
