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
from typing import Any, Dict, Final

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, status
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from . import runtime_cfg
from .fastapi_deps import get_async_db
from .orm.tables import PushedAuthorizationRequest

router = APIRouter()

DEFAULT_PAR_EXPIRY = 90  # seconds

RFC9126_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc9126"


async def store_par_request(
    params: Dict[str, Any],
    db: AsyncSession,
    expires_in: int = DEFAULT_PAR_EXPIRY,
) -> str:
    """Store *params* and return a unique ``request_uri``."""

    request_uri = f"urn:ietf:params:oauth:request_uri:{uuid.uuid4()}"
    expires_at = datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)
    await PushedAuthorizationRequest.handlers.par.core(
        {
            "db": db,
            "payload": {
                "request_uri": request_uri,
                "params": params,
                "expires_at": expires_at,
            },
        }
    )
    return request_uri


async def get_par_request(request_uri: str, db: AsyncSession) -> Dict[str, Any] | None:
    """Retrieve parameters for *request_uri* if present and not expired."""

    obj = await db.get(PushedAuthorizationRequest, request_uri)
    if not obj:
        return None
    if datetime.now(tz=timezone.utc) > obj.expires_at:
        await PushedAuthorizationRequest.handlers.delete.core({"db": db, "obj": obj})
        return None
    return obj.params


async def reset_par_store(db: AsyncSession) -> None:
    """Clear stored pushed authorization requests (test helper)."""

    await db.execute(delete(PushedAuthorizationRequest))
    await db.commit()


@router.post("/par", status_code=status.HTTP_201_CREATED)
async def pushed_authorization_request(
    request: Request, db: AsyncSession = Depends(get_async_db)
):
    """Endpoint for RFC 9126 pushed authorization requests."""

    if not runtime_cfg.settings.enable_rfc9126:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "PAR disabled")
    form = await request.form()
    request_uri = await store_par_request(dict(form), db)
    return {"request_uri": request_uri, "expires_in": DEFAULT_PAR_EXPIRY}


def include_rfc9126(app: FastAPI) -> None:
    """Attach the RFC 9126 router to *app* if enabled."""

    if runtime_cfg.settings.enable_rfc9126 and not any(
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
