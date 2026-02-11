from __future__ import annotations

from urllib.parse import parse_qs

from tigrbl_auth.deps import TigrblApi, HTTPException, Request, status

from ..runtime_cfg import settings
from ..routers.shared import _require_tls
from ..rfc.rfc7662 import introspect_token

api = TigrblApi()
router = api


@api.post("/introspect")
async def introspect(request: Request):
    _require_tls(request)
    if not settings.enable_rfc7662:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "introspection disabled")
    token = None
    if hasattr(request, "form"):
        form = await request.form()
        token = form.get("token")
    elif hasattr(request, "body"):
        body = request.body.decode("utf-8") if request.body else ""
        parsed = parse_qs(body, keep_blank_values=True)
        values = parsed.get("token")
        token = values[0] if values else None
    if not token:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "token parameter required")
    data = introspect_token(token)
    return data
