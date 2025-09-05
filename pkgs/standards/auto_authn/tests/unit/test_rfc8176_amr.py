"""Tests for Authentication Method Reference validation (RFC 8176).

The :func:`auto_authn.rfc8176.validate_amr_claim` helper ensures that
``amr`` claim values adhere to the registry defined in :rfc:`8176`.
"""

import pytest

from auto_authn.rfc8176 import RFC8176_SPEC_URL, validate_amr_claim
from auto_authn.runtime_cfg import settings


@pytest.mark.unit
def test_valid_amr_values_enabled():
    """Known values pass validation when the feature is enabled."""
    assert validate_amr_claim(["pwd", "otp"], enabled=True)


@pytest.mark.unit
def test_invalid_amr_values_enabled():
    """Unknown values fail validation when the feature is enabled."""
    assert not validate_amr_claim(["pwd", "unknown"], enabled=True)


@pytest.mark.unit
def test_invalid_amr_values_disabled():
    """When disabled, validation accepts any values."""
    assert validate_amr_claim(["unknown"], enabled=False)


@pytest.mark.unit
def test_respects_runtime_setting(monkeypatch):
    """Default behaviour follows the runtime configuration toggle."""
    monkeypatch.setattr(settings, "enable_rfc8176", False)
    assert validate_amr_claim(["bogus"])  # disabled -> accepts
    monkeypatch.setattr(settings, "enable_rfc8176", True)
    assert not validate_amr_claim(["bogus"])  # enabled -> rejects


@pytest.mark.unit
def test_spec_url_constant():
    """Spec URL constant references the official RFC document."""
    assert RFC8176_SPEC_URL.endswith("rfc8176")
