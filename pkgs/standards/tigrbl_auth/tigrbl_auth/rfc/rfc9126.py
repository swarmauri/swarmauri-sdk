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
from typing import TYPE_CHECKING, Any, Dict, Final

from tigrbl_auth.deps import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
    AsyncSession,
)

from ..db import get_db
from ..runtime_cfg import settings

if TYPE_CHECKING:  # pragma: no cover
    pass

DEFAULT_PAR_EXPIRY = 90  # seconds

RFC9126_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc9126"


router = APIRouter()


@router.post("/par", status_code=status.HTTP_201_CREATED)
async def pushed_authorization_request(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Handle Pushed Authorization Requests.

    Stores the incoming parameters and returns a ``request_uri`` pointing to the
    stored request along with the remaining lifetime in seconds.
    Returns HTTP 404 when the feature is disabled.
    """

    if not settings.enable_rfc9126:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "PAR disabled")
    params = dict(await request.form())
    if db is None:
        request_uri = f"urn:ietf:params:oauth:request_uri:{uuid.uuid4()}"
    else:
        request_uri = await store_par_request(params, db, DEFAULT_PAR_EXPIRY)
    return {"request_uri": request_uri, "expires_in": DEFAULT_PAR_EXPIRY}


async def store_par_request(
    params: Dict[str, Any],
    db: AsyncSession,
    expires_in: int = DEFAULT_PAR_EXPIRY,
) -> str:
    """Store *params* and return a unique ``request_uri``."""

    from ..orm import PushedAuthorizationRequest

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

    from ..orm import PushedAuthorizationRequest

    obj = await PushedAuthorizationRequest.handlers.read.core(
        {"db": db, "obj_id": request_uri}
    )
    if not obj:
        return None
    expires_at = obj.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if datetime.now(tz=timezone.utc) > expires_at:
        await PushedAuthorizationRequest.handlers.delete.core({"db": db, "obj": obj})
        return None
    return obj.params


async def reset_par_store(db: AsyncSession) -> None:
    """Clear stored pushed authorization requests (test helper)."""

    from ..orm import PushedAuthorizationRequest

    await PushedAuthorizationRequest.handlers.clear.core({"db": db})


__all__ = [
    "store_par_request",
    "get_par_request",
    "reset_par_store",
    "DEFAULT_PAR_EXPIRY",
    "RFC9126_SPEC_URL",
    "router",
]
