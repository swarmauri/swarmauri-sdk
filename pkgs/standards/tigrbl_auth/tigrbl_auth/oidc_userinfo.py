"""UserInfo endpoint for OpenID Connect 1.0.

This module implements the `/userinfo` endpoint as described in the
OpenID Connect Core specification.  It is **not** tied to an RFC so it
lives in the OIDC namespace instead of an `rfcXXXX` module.

The endpoint returns a set of claims about the authenticated user based
on the scopes granted to the access token.  Unrequested claim groups are
omitted from the response.
"""

from __future__ import annotations

from .deps import (
    APIRouter,
    Depends,
    FastAPI,
    HTTPException,
    Request,
    Response,
    status,
)

from .fastapi_deps import get_current_principal
from .jwtoken import JWTCoder, InvalidTokenError, _svc
from .orm import User
from .rfc.rfc6750 import extract_bearer_token
from .deps import JWAAlg

router = APIRouter()


@router.get("/userinfo", response_model=None)
async def userinfo(
    request: Request, user: User = Depends(get_current_principal)
) -> Response | dict[str, str]:
    """Return claims about the authenticated user.

    The caller must present a valid access token in the ``Authorization``
    header.  Returned claims are filtered based on scopes granted in that
    token.  If the request ``Accept`` header includes ``application/jwt`` the
    response will be JWS signed.
    """

    token = await extract_bearer_token(
        request, request.headers.get("Authorization", "")
    )
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing access token")
    try:
        payload = await JWTCoder.default().async_decode(token)
    except InvalidTokenError as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "invalid access token"
        ) from exc
    scopes: set[str] = set(payload.get("scope", "").split())

    claims: dict[str, str] = {"sub": str(user.id)}
    if "profile" in scopes:
        claims["name"] = user.username
    if "email" in scopes:
        claims["email"] = user.email
    if "address" in scopes and getattr(user, "address", None):
        claims["address"] = getattr(user, "address")
    if "phone" in scopes and getattr(user, "phone", None):
        claims["phone_number"] = getattr(user, "phone")

    if "application/jwt" in request.headers.get("accept", ""):
        svc, kid = _svc()
        token = await svc.mint(claims, alg=JWAAlg.EDDSA, kid=kid)
        return Response(content=token, media_type="application/jwt")

    return claims


# ---------------------------------------------------------------------------
# FastAPI integration
# ---------------------------------------------------------------------------


def include_oidc_userinfo(app: FastAPI) -> None:
    """Attach the UserInfo endpoint to *app* if not already present."""

    if not any(route.path == "/userinfo" for route in app.routes):
        app.include_router(router)


__all__ = ["router", "include_oidc_userinfo"]
