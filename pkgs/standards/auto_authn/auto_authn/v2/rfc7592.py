"""Utilities for OAuth 2.0 Dynamic Client Registration Management (RFC 7592).

Helpers for updating and deleting clients registered via RFC 7591.
Functionality can be toggled using ``runtime_cfg.Settings.enable_rfc7592``.
"""

from __future__ import annotations

from typing import Final

from .runtime_cfg import settings
from . import rfc7591

# Public URL for the RFC specification
RFC7592_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc7592"


def update_client(
    client_id: str, updates: dict, *, enabled: bool | None = None
) -> dict:
    """Update metadata for a registered client and return the new record.

    Raises ``RuntimeError`` if RFC 7592 support is disabled and ``KeyError``
    if the client is unknown.
    """

    if enabled is None:
        enabled = settings.enable_rfc7592
    if not enabled:
        raise RuntimeError("RFC 7592 support is disabled")
    client = rfc7591.get_client(client_id)
    if client is None:
        raise KeyError("unknown client")
    client.update(updates)
    return client


def delete_client(client_id: str, *, enabled: bool | None = None) -> bool:
    """Remove *client_id* from the registry. Return ``True`` if removed."""

    if enabled is None:
        enabled = settings.enable_rfc7592
    if not enabled:
        raise RuntimeError("RFC 7592 support is disabled")
    return rfc7591._CLIENT_REGISTRY.pop(client_id, None) is not None


__all__ = [
    "update_client",
    "delete_client",
    "RFC7592_SPEC_URL",
]
