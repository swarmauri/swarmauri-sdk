"""Tests for RFC 8252 compliance.

The OAuth 2.0 for Native Apps specification (RFC 8252) outlines requirements
such as PKCE and loopback redirect URIs. These tests capture the expected
behaviour and are marked xfail until full support is implemented.
"""

import pytest


@pytest.mark.unit
class TestRFC8252Compliance:
    """Verify planned RFC 8252 support."""

    @pytest.mark.xfail(
        reason="Loopback redirect URIs (RFC 8252) not implemented; feature planned."
    )
    def test_loopback_redirect_uri_support(self) -> None:
        """Ensure loopback redirect URIs are accepted."""
        pytest.fail("RFC 8252 loopback redirect URIs not implemented")

    @pytest.mark.xfail(
        reason="PKCE enforcement for public clients (RFC 8252) not implemented; feature planned."
    )
    def test_pkce_required_for_public_clients(self) -> None:
        """Ensure public clients must use PKCE."""
        pytest.fail("RFC 8252 PKCE enforcement not implemented")
