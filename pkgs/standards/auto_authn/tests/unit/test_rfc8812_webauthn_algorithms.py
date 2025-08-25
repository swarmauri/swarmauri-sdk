"""Tests for WebAuthn algorithm registrations (RFC 8812).

The tests ensure that only algorithms registered by RFC 8812 are accepted when
its feature flag is enabled and that any algorithm is allowed when the feature
is disabled.
"""

import pytest

from auto_authn.v2 import runtime_cfg, supported_algorithms
from auto_authn.v2.rfc8812 import WEBAUTHN_ALGORITHMS, is_webauthn_algorithm

EXPECTED_ALGORITHMS = {
    "RS256",
    "RS384",
    "RS512",
    "RS1",
    "PS256",
    "PS384",
    "PS512",
    "ES256",
    "ES384",
    "ES512",
    "ES256K",
}


@pytest.mark.unit
def test_known_algorithms_allowed(monkeypatch):
    """Algorithms listed in RFC 8812 pass validation when enabled."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc8812", True)
    assert WEBAUTHN_ALGORITHMS == EXPECTED_ALGORITHMS
    for alg in WEBAUTHN_ALGORITHMS:
        assert is_webauthn_algorithm(alg)
    assert not is_webauthn_algorithm("HS256")


@pytest.mark.unit
def test_supported_algorithms_extends_when_enabled(monkeypatch):
    """Supported algorithm list includes RFC 8812 entries when enabled."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc8812", True)
    algs = supported_algorithms()
    for alg in WEBAUTHN_ALGORITHMS:
        assert alg in algs
    assert "PS256" in algs
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc8812", False)
    algs = supported_algorithms()
    assert not any(alg in algs for alg in WEBAUTHN_ALGORITHMS)


@pytest.mark.unit
def test_disabled_allows_any_alg(monkeypatch):
    """When disabled, validation always succeeds."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc8812", False)
    assert is_webauthn_algorithm("HS256")
    assert is_webauthn_algorithm("unknown")
