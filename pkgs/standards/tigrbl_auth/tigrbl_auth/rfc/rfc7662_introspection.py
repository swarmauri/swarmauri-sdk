from __future__ import annotations

from tigrbl_auth.deps import TigrblApi, HTTPException, Request, status

from ..runtime_cfg import settings
from ..routers.schemas import IntrospectOut
from ..routers.shared import _require_tls
from ..rfc.rfc7662 import introspect_token

api = TigrblApi()
router = api


@api.post("/introspect", response_model=IntrospectOut)
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
