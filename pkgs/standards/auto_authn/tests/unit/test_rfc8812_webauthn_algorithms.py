"""Tests for RFC 8812: WebAuthn algorithm registrations."""

import pytest

from auto_authn.v2 import runtime_cfg
from auto_authn.v2.rfc8812 import (
    RFC8812_SPEC_URL,
    WEBAUTHN_ALGORITHMS,
    is_webauthn_algorithm,
)


@pytest.mark.unit
def test_algorithm_lookup_enabled() -> None:
    """Known algorithms are recognised when the feature is enabled."""
    assert is_webauthn_algorithm("ES256K", enabled=True)
    assert not is_webauthn_algorithm("UNKNOWN", enabled=True)


@pytest.mark.unit
def test_feature_toggle(monkeypatch) -> None:
    """When disabled, any algorithm is accepted."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc8812", False)
    assert is_webauthn_algorithm("UNKNOWN")
    assert is_webauthn_algorithm("ES256K")
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc8812", True)
    assert "ES256K" in WEBAUTHN_ALGORITHMS


def test_spec_url_constant() -> None:
    """Expose the spec URL for documentation purposes."""
    assert "8812" in RFC8812_SPEC_URL
