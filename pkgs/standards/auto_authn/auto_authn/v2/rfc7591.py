"""Utilities for OAuth 2.0 Dynamic Client Registration (RFC 7591).

This module provides a minimal in-memory client registry to illustrate
compliance with RFC 7591. Functionality can be toggled via
``runtime_cfg.Settings.enable_rfc7591`` so deployments may opt in or out
as needed.
"""

from __future__ import annotations

import secrets
from typing import Dict, Final

from .runtime_cfg import settings

# In-memory registry of dynamically registered clients
_CLIENT_REGISTRY: Dict[str, dict] = {}

# Public URL for the RFC specification
RFC7591_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc7591"


def register_client(metadata: dict, *, enabled: bool | None = None) -> dict:
    """Register a new OAuth client as described in RFC 7591.

    Parameters
    ----------
    metadata: dict
        Client metadata defined by RFC 7591 §2.
    enabled: bool | None
        Override global toggle for RFC 7591.

    Returns
    -------
    dict
        The stored client metadata including generated credentials.

    Raises
    ------
    RuntimeError
        If RFC 7591 support is disabled.
    """

    if enabled is None:
        enabled = settings.enable_rfc7591
    if not enabled:
        raise RuntimeError("RFC 7591 support is disabled")

    client_id = secrets.token_urlsafe(16)
    client_secret = secrets.token_urlsafe(32)
    data = {"client_id": client_id, "client_secret": client_secret, **metadata}
    _CLIENT_REGISTRY[client_id] = data
    return data


def get_client(client_id: str) -> dict | None:
    """Return metadata for *client_id* or ``None`` if unknown."""

    return _CLIENT_REGISTRY.get(client_id)


def reset_client_registry() -> None:
    """Clear the in-memory client registry (primarily for tests)."""

    _CLIENT_REGISTRY.clear()


__all__ = [
    "register_client",
    "get_client",
    "reset_client_registry",
    "RFC7591_SPEC_URL",
]
