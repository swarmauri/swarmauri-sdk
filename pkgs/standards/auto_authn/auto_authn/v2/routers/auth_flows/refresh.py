"""Token refresh endpoint."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from .common import RefreshIn, TokenPair, _jwt, _require_tls

router = APIRouter()


@router.post("/token/refresh", response_model=TokenPair)
async def refresh(body: RefreshIn, request: Request):
    _require_tls(request)
    try:
        access, refresh_token = _jwt.refresh(body.refresh_token)
    except Exception:  # noqa: BLE001
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid refresh token")
    return TokenPair(access_token=access, refresh_token=refresh_token)
