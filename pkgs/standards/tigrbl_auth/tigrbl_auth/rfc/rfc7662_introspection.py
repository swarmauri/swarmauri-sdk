from __future__ import annotations

from urllib.parse import parse_qs

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
    form_data = parse_qs((request.body or b"").decode("utf-8"), keep_blank_values=True)
    token_values = form_data.get("token") or []
    token = token_values[0] if token_values else None
    if not token:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "token parameter required")
    return introspect_token(token)
