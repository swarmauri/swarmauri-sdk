"""Unit tests for OAuth 2.0 Dynamic Client Registration Management (RFC 7592).

These tests ensure that client metadata can be updated or removed when RFC 7592
support is enabled and that operations are rejected when disabled.
"""

from unittest.mock import patch

import pytest

from auto_authn import rfc7591, rfc7592


def test_update_and_delete_client_when_enabled() -> None:
    """Clients may be updated and deleted when RFC 7592 is enabled."""

    with (
        patch.object(rfc7591.settings, "enable_rfc7591", True),
        patch.object(rfc7592.settings, "enable_rfc7592", True),
    ):
        rfc7591.reset_client_registry()
        client = rfc7591.register_client({})
        updated = rfc7592.update_client(client["client_id"], {"client_name": "example"})
        assert updated["client_name"] == "example"
        assert rfc7592.delete_client(client["client_id"]) is True
        assert rfc7591.get_client(client["client_id"]) is None


def test_update_client_disabled_raises() -> None:
    """Updating a client fails when RFC 7592 support is disabled."""

    with patch.object(rfc7591.settings, "enable_rfc7591", True):
        rfc7591.reset_client_registry()
        client = rfc7591.register_client({})
    with patch.object(rfc7592.settings, "enable_rfc7592", False):
        with pytest.raises(RuntimeError):
            rfc7592.update_client(client["client_id"], {})


def test_delete_client_disabled_raises() -> None:
    """Deleting a client fails when RFC 7592 support is disabled."""

    with patch.object(rfc7591.settings, "enable_rfc7591", True):
        rfc7591.reset_client_registry()
        client = rfc7591.register_client({})
    with patch.object(rfc7592.settings, "enable_rfc7592", False):
        with pytest.raises(RuntimeError):
            rfc7592.delete_client(client["client_id"])
