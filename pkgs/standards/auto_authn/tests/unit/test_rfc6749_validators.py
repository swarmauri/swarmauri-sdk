"""Unit tests for RFC 6749 validation helpers."""

import pytest

from auto_authn.v2.rfc6749 import (
    RFC6749Error,
    enforce_grant_type,
    enforce_password_grant,
)
from auto_authn.v2.runtime_cfg import settings


@pytest.fixture()
def toggle_rfc6749():
    original = settings.enable_rfc6749
    settings.enable_rfc6749 = True
    try:
        yield
    finally:
        settings.enable_rfc6749 = original


@pytest.mark.unit
def test_enforce_grant_type_validates_when_enabled(toggle_rfc6749):
    """RFC 6749 §5.2 requires ``grant_type`` presence and support."""
    with pytest.raises(RFC6749Error):
        enforce_grant_type(None, {"password"})
    with pytest.raises(RFC6749Error):
        enforce_grant_type("client_credentials", {"password"})


@pytest.mark.unit
def test_enforce_password_grant_requires_credentials(toggle_rfc6749):
    """RFC 6749 §4.3 mandates ``username`` and ``password``."""
    with pytest.raises(RFC6749Error):
        enforce_password_grant({"username": "user"})
    with pytest.raises(RFC6749Error):
        enforce_password_grant({"password": "pass"})


@pytest.mark.unit
def test_enforcement_noop_when_disabled():
    """Validation helpers are skipped when RFC 6749 enforcement is disabled."""
    original = settings.enable_rfc6749
    settings.enable_rfc6749 = False
    try:
        enforce_grant_type(None, {"password"})
        enforce_password_grant({})
    finally:
        settings.enable_rfc6749 = original
