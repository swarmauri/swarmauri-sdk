from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, Request, status
from pydantic import BaseModel
from ...typing import StrUUID

from ...rfc7662 import introspect_token
from ...runtime_cfg import settings
from .common import _require_tls, router


class IntrospectOut(BaseModel):
    active: bool
    sub: Optional[StrUUID] = None
    tid: Optional[StrUUID] = None
    kind: Optional[str] = None


@router.post("/introspect", response_model=IntrospectOut)
async def introspect(request: Request):
    _require_tls(request)
    if not settings.enable_rfc7662:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "introspection disabled")
    form = await request.form()
    token = form.get("token")
    if not token:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "token parameter required")
    data = introspect_token(token)
    return IntrospectOut(**data)
