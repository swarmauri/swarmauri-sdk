"""Tests for Authentication Method Reference validation (RFC 8176).

The :func:`auto_authn.v2.rfc8176.validate_amr_claim` helper ensures that
``amr`` claim values adhere to the registry defined in :rfc:`8176`.
"""

import pytest

from auto_authn.v2.rfc8176 import validate_amr_claim


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
