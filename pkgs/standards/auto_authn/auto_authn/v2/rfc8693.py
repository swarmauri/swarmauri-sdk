"""Utilities for OAuth 2.0 Token Exchange (RFC 8693).

This module provides a minimal token exchange endpoint to illustrate
compliance with RFC 8693. The endpoint can be toggled on or off via the
``enable_rfc8693`` setting in ``runtime_cfg.Settings``.

See RFC 8693: https://www.rfc-editor.org/rfc/rfc8693
"""

from __future__ import annotations

from typing import Final

from fastapi import APIRouter, FastAPI, Form, HTTPException, status

from .runtime_cfg import settings

RFC8693_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc8693"

router = APIRouter()


def exchange_token(subject_token: str) -> str:
    """Return a dummy exchanged token for *subject_token*.

    Raises ``RuntimeError`` if RFC 8693 support is disabled.
    """
    if not settings.enable_rfc8693:
        raise RuntimeError("RFC 8693 support disabled")
    return f"exchanged-{subject_token}"


@router.post("/token/exchange")
async def token_exchange(
    subject_token: str = Form(...),
    subject_token_type: str = Form(...),
) -> dict[str, str]:
    """RFC 8693 token exchange endpoint.

    Returns a new access token derived from ``subject_token``.
    """
    if not settings.enable_rfc8693:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "token exchange disabled")
    new_token = exchange_token(subject_token)
    return {
        "access_token": new_token,
        "issued_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "token_type": "bearer",
    }


def include_rfc8693(app: FastAPI) -> None:
    """Attach the RFC 8693 router to *app* if enabled."""
    if settings.enable_rfc8693 and not any(
        route.path == "/token/exchange" for route in app.routes
    ):
        app.include_router(router)


__all__ = [
    "exchange_token",
    "router",
    "include_rfc8693",
    "RFC8693_SPEC_URL",
]
