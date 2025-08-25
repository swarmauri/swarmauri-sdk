"""Unit tests for OAuth 2.0 Dynamic Client Registration Protocol (RFC 7591).

These tests verify that the minimal client registration helpers behave as
specified when RFC 7591 support is toggled on or off.
"""

from unittest.mock import patch

import pytest

from auto_authn.v2 import rfc7591


def test_register_client_when_enabled() -> None:
    """Registration succeeds and client is stored when RFC 7591 is enabled."""

    with patch.object(rfc7591.settings, "enable_rfc7591", True):
        rfc7591.reset_client_registry()
        client = rfc7591.register_client({"redirect_uris": ["https://a.example/cb"]})
        assert "client_id" in client
        stored = rfc7591.get_client(client["client_id"])
        assert stored is not None
        assert stored["redirect_uris"] == ["https://a.example/cb"]


def test_register_client_disabled_raises() -> None:
    """Registration is rejected when RFC 7591 support is disabled."""

    with patch.object(rfc7591.settings, "enable_rfc7591", False):
        with pytest.raises(RuntimeError):
            rfc7591.register_client({})
