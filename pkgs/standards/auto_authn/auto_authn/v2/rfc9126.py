"""Pushed Authorization Requests support (RFC 9126).

This module implements a minimal in-memory store for OAuth 2.0 Pushed
Authorization Requests (PAR) as defined in RFC 9126. The feature can be
enabled or disabled via ``settings.enable_rfc9126`` in
``runtime_cfg.Settings``.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Dict, Tuple, Any

# In-memory storage mapping request_uri -> (params, expiry)
_PAR_STORE: Dict[str, Tuple[Dict[str, Any], datetime]] = {}

DEFAULT_PAR_EXPIRY = 90  # seconds


def store_par_request(
    params: Dict[str, Any], expires_in: int = DEFAULT_PAR_EXPIRY
) -> str:
    """Store *params* and return a unique ``request_uri``.

    Parameters expire after *expires_in* seconds.
    """
    request_uri = f"urn:ietf:params:oauth:request_uri:{uuid.uuid4()}"
    _PAR_STORE[request_uri] = (
        params,
        datetime.utcnow() + timedelta(seconds=expires_in),
    )
    return request_uri


def get_par_request(request_uri: str) -> Dict[str, Any] | None:
    """Retrieve parameters for *request_uri* if present and not expired."""
    record = _PAR_STORE.get(request_uri)
    if not record:
        return None
    params, expiry = record
    if datetime.utcnow() > expiry:
        del _PAR_STORE[request_uri]
        return None
    return params


def reset_par_store() -> None:
    """Clear stored pushed authorization requests (test helper)."""
    _PAR_STORE.clear()


__all__ = [
    "store_par_request",
    "get_par_request",
    "reset_par_store",
    "DEFAULT_PAR_EXPIRY",
]
