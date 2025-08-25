"""Pushed Authorization Requests support (RFC 9126).

This module implements a minimal in-memory store for OAuth 2.0 Pushed
Authorization Requests (PAR) as defined in RFC 9126. The feature can be
enabled or disabled via ``settings.enable_rfc9126`` in
``runtime_cfg.Settings``.

See RFC 9126: https://www.rfc-editor.org/rfc/rfc9126
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Final, Tuple

from fastapi import APIRouter, FastAPI, HTTPException, Request, status

from .runtime_cfg import settings

# In-memory storage mapping request_uri -> (params, expiry)
_PAR_STORE: Dict[str, Tuple[Dict[str, Any], datetime]] = {}

router = APIRouter()

DEFAULT_PAR_EXPIRY = 90  # seconds

RFC9126_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc9126"


def store_par_request(
    params: Dict[str, Any], expires_in: int = DEFAULT_PAR_EXPIRY
) -> str:
    """Store *params* and return a unique ``request_uri``.

    Parameters expire after *expires_in* seconds.
    """
    request_uri = f"urn:ietf:params:oauth:request_uri:{uuid.uuid4()}"
    _PAR_STORE[request_uri] = (
        params,
        datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in),
    )
    return request_uri


def get_par_request(request_uri: str) -> Dict[str, Any] | None:
    """Retrieve parameters for *request_uri* if present and not expired."""
    record = _PAR_STORE.get(request_uri)
    if not record:
        return None
    params, expiry = record
    if datetime.now(tz=timezone.utc) > expiry:
        del _PAR_STORE[request_uri]
        return None
    return params


def reset_par_store() -> None:
    """Clear stored pushed authorization requests (test helper)."""
    _PAR_STORE.clear()


@router.post("/par", status_code=status.HTTP_201_CREATED)
async def pushed_authorization_request(request: Request):
    """Endpoint for RFC 9126 pushed authorization requests."""

    if not settings.enable_rfc9126:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "PAR disabled")
    form = await request.form()
    request_uri = store_par_request(dict(form))
    return {"request_uri": request_uri, "expires_in": DEFAULT_PAR_EXPIRY}


def include_rfc9126(app: FastAPI) -> None:
    """Attach the RFC 9126 router to *app* if enabled."""

    if settings.enable_rfc9126 and not any(
        route.path == "/par" for route in app.routes
    ):
        app.include_router(router)


__all__ = [
    "store_par_request",
    "get_par_request",
    "reset_par_store",
    "DEFAULT_PAR_EXPIRY",
    "RFC9126_SPEC_URL",
    "router",
    "include_rfc9126",
]
