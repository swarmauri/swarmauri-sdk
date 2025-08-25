"""Tests for Client-Initiated Backchannel Authentication (RFC 8812).

These tests verify that :func:`auto_authn.v2.rfc8812.validate_ciba_request`
checks for the required end-user hint and honours the feature toggle.
"""

import pytest

from auto_authn.v2.rfc8812 import validate_ciba_request, RFC8812_SPEC_URL


@pytest.mark.unit
def test_validation_requires_hint():
    """A CIBA request must include an end-user hint when enabled."""
    request = {"login_hint": "user@example.com"}
    assert validate_ciba_request(request, enabled=True)
    assert not validate_ciba_request({}, enabled=True)


@pytest.mark.unit
def test_feature_toggle_disables_validation():
    """When disabled, validation is bypassed."""
    assert validate_ciba_request({}, enabled=False)


@pytest.mark.unit
def test_spec_url_constant():
    """Expose the RFC 8812 specification URL."""
    assert RFC8812_SPEC_URL.endswith("rfc8812")
