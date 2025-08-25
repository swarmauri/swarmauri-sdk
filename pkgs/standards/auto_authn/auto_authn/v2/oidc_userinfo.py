"""UserInfo endpoint for OpenID Connect 1.0.

This module implements the `/userinfo` endpoint as described in the
OpenID Connect Core specification.  It is **not** tied to an RFC so it
lives in the OIDC namespace instead of an `rfcXXXX` module.

The endpoint returns a minimal set of claims about the authenticated
user.  Currently the returned claims are a subset of those advertised in
the discovery document.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi import FastAPI

from .fastapi_deps import get_current_principal
from .orm.tables import User

router = APIRouter()


@router.get("/userinfo")
async def userinfo(user: User = Depends(get_current_principal)) -> dict[str, str]:
    """Return claims about the authenticated user.

    The caller must present a valid access token in the `Authorization`
    header.  For now, the response includes only a subset of standard
    claims.
    """

    return {
        "sub": str(user.id),
        "name": user.username,
        "email": user.email,
    }


# ---------------------------------------------------------------------------
# FastAPI integration
# ---------------------------------------------------------------------------


def include_oidc_userinfo(app: FastAPI) -> None:
    """Attach the UserInfo endpoint to *app* if not already present."""

    if not any(route.path == "/userinfo" for route in app.routes):
        app.include_router(router)


__all__ = ["router", "include_oidc_userinfo"]
