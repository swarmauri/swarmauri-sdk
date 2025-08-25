"""Tests for OAuth 2.0 Device Authorization Grant (RFC 8628).

RFC excerpt (RFC 8628 §6.1):

The client SHOULD generate a user code that is easy to read and type and
that is at least 8 characters long and consists of upper-case letters and
digits.
"""

import pytest

from auto_authn.v2 import generate_device_code, generate_user_code, validate_user_code
import auto_authn.v2.rfc8628 as rfc8628_mod


@pytest.mark.unit
def test_generate_user_code_matches_rfc8628_requirements():
    """Generated user_code satisfies RFC 8628 §6.1."""

    code = generate_user_code()
    assert len(code) == 8
    assert code.isupper() and code.isalnum()


@pytest.mark.unit
def test_validate_user_code_accepts_valid():
    """validate_user_code returns True for valid codes."""

    code = "ABC12345"
    assert validate_user_code(code)


@pytest.mark.unit
def test_validate_user_code_rejects_invalid():
    """Invalid user_code values are rejected when enabled."""

    assert not validate_user_code("bad-code")
    assert not validate_user_code("SHORT")


@pytest.mark.unit
def test_validation_skipped_when_disabled(monkeypatch):
    """When RFC 8628 is disabled validation always passes."""

    monkeypatch.setattr(rfc8628_mod.settings, "enable_rfc8628", False)
    assert validate_user_code("bad-code")


@pytest.mark.unit
def test_generate_device_code_characteristics():
    """Generated device_code is URL-safe and sufficiently long."""

    code = generate_device_code()
    assert len(code) >= 43
    allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
    assert all(ch in allowed for ch in code)
