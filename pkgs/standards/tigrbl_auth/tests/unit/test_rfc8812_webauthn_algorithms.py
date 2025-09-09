"""Tests for WebAuthn algorithm registrations (RFC 8812).

The tests ensure that only algorithms registered by RFC 8812 are accepted when
its feature flag is enabled and that any algorithm is allowed when the feature
is disabled.
"""

import pytest

from tigrbl_auth import runtime_cfg, supported_algorithms
from tigrbl_auth.rfc8812 import WEBAUTHN_ALGORITHMS, is_webauthn_algorithm

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
    assert "RS256" in algs
    assert not any(alg in algs for alg in WEBAUTHN_ALGORITHMS - {"RS256"})


@pytest.mark.unit
def test_disabled_allows_any_alg(monkeypatch):
    """When disabled, validation always succeeds."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc8812", False)
    assert is_webauthn_algorithm("HS256")
    assert is_webauthn_algorithm("unknown")


@pytest.mark.unit
def test_non_string_algorithm_rejected(monkeypatch):
    """Non-string algorithm identifiers are rejected when enabled."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc8812", True)
    assert not is_webauthn_algorithm(None)  # type: ignore[arg-type]
    assert not is_webauthn_algorithm(123)  # type: ignore[arg-type]


@pytest.mark.unit
def test_case_insensitive(monkeypatch):
    """Algorithm comparison is case-insensitive."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc8812", True)
    assert is_webauthn_algorithm("es256")
