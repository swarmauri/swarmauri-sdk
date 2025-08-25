from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from ...rfc7662 import introspect_token
from ...runtime_cfg import settings
from .common import require_tls

router = APIRouter()


class IntrospectOut(BaseModel):
    active: bool
    sub: str | None = None
    tid: str | None = None
    kind: str | None = None


@router.post("/introspect", response_model=IntrospectOut)
async def introspect(request: Request):
    require_tls(request)
    if not settings.enable_rfc7662:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "introspection disabled")
    form = await request.form()
    token = form.get("token")
    if not token:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "token parameter required")
    data = introspect_token(token)
    return IntrospectOut(**data)
