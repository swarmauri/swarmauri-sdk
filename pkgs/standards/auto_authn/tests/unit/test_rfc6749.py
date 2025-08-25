"""Tests for OAuth 2.0 core compliance (RFC 6749).

These tests verify that the optional RFC 6749 feature enforces required token
request parameters when enabled.
"""

import pytest

from auto_authn.v2 import RFC6749ComplianceError, validate_token_request
from auto_authn.v2.runtime_cfg import settings

RFC6749_URL = "https://www.rfc-editor.org/rfc/rfc6749"


def test_token_request_validation_enforced(enable_rfc6749):
    """RFC 6749 requires ``grant_type`` and ``client_id`` in token requests."""
    with pytest.raises(RFC6749ComplianceError):
        validate_token_request({"client_id": "abc"})
    with pytest.raises(RFC6749ComplianceError):
        validate_token_request({"grant_type": "authorization_code"})


def test_token_request_validation_disabled():
    """Validation is skipped when RFC 6749 enforcement is disabled."""
    original = settings.enable_rfc6749
    settings.enable_rfc6749 = False
    try:
        validate_token_request({"client_id": "abc"})
        validate_token_request({"grant_type": "authorization_code"})
    finally:
        settings.enable_rfc6749 = original
