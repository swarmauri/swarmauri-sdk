from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import UUID, uuid4
from urllib.parse import urlencode

from tigrbl_auth.deps import (
    Depends,
    HTTPException,
    Request,
    status,
    HTMLResponse,
    RedirectResponse,
    AsyncSession,
)

from ...fastapi_deps import get_db
from ...orm import AuthCode, Client, User
from ...oidc_id_token import mint_id_token, oidc_hash
from ...rfc8414_metadata import ISSUER
from ...rfc8252 import is_native_redirect_uri
from ..shared import _require_tls, SESSIONS, AUTH_CODES
from . import router


@router.get("/authorize")
async def authorize(
    response_type: str,
    client_id: str,
    redirect_uri: str,
    scope: str,
    request: Request,
    response_mode: Optional[str] = None,
    state: Optional[str] = None,
    nonce: Optional[str] = None,
    code_challenge: Optional[str] = None,
    code_challenge_method: Optional[str] = None,
    prompt: Optional[str] = None,
    max_age: Optional[int] = None,
    login_hint: Optional[str] = None,
    claims: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    _require_tls(request)
    rts = set(response_type.split())
    allowed = {"code", "token", "id_token"}
    if not rts or not rts.issubset(allowed):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, {"error": "unsupported_response_type"}
        )
    scopes = set(scope.split())
    if "openid" not in scopes:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "invalid_scope"})
    if "id_token" in rts and not nonce:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "invalid_request"})
    try:
        client_uuid = UUID(client_id)
    except ValueError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "invalid_request"})
    client = await db.get(Client, client_uuid)
    if client is None or redirect_uri not in (client.redirect_uris or "").split():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "invalid_request"})

    prompts = set(prompt.split()) if prompt else set()
    sid = request.cookies.get("sid")
    session = SESSIONS.get(sid) if sid else None
    if login_hint and session and session.get("username") != login_hint:
        session = None
    if "login" in prompts:
        session = None
    if session is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, {"error": "login_required"})
    if max_age is not None:
        auth_time = session.get("auth_time")
        if auth_time is None or datetime.now(timezone.utc) - auth_time > timedelta(
            seconds=max_age
        ):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, {"error": "login_required"}
            )
    user_sub = session["sub"]
    tenant_id = session["tid"]

    if is_native_redirect_uri(redirect_uri) and not code_challenge:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "invalid_request"})
    if code_challenge_method and code_challenge_method != "S256":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "invalid_request"})
    mode = response_mode or ("fragment" if rts & {"token", "id_token"} else "query")
    if mode not in {"query", "fragment", "form_post"}:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, {"error": "unsupported_response_mode"}
        )
    params: list[tuple[str, str]] = []
    code: str | None = None
    access: str | None = None
    scope_str = " ".join(sorted(scopes))
    requested_claims: dict[str, Any] | None = None
    if claims:
        try:
            parsed_claims = json.loads(claims)
            if not isinstance(parsed_claims, dict):
                raise ValueError
            requested_claims = parsed_claims
        except Exception:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, {"error": "invalid_request"}
            )
    if "code" in rts:
        code = uuid4()
        payload = {
            "code": code,
            "user_id": UUID(user_sub),
            "tenant_id": UUID(tenant_id),
            "client_id": UUID(client_id),
            "redirect_uri": redirect_uri,
            "code_challenge": code_challenge,
            "nonce": nonce,
            "scope": scope_str,
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10),
        }
        if requested_claims:
            payload["claims"] = requested_claims
        await AuthCode.handlers.create.core({"db": db, "payload": payload})
        await db.commit()
        AUTH_CODES[str(code)] = payload
        params.append(("code", str(code)))
    if "token" in rts:
        from ..shared import _jwt

        access = await _jwt.async_sign(sub=user_sub, tid=tenant_id, scope=scope_str)
        params.append(("access_token", access))
        params.append(("token_type", "bearer"))
    if "id_token" in rts:
        extra_claims: dict[str, Any] = {"tid": tenant_id, "typ": "id"}
        if requested_claims and "id_token" in requested_claims:
            user_obj = await db.get(User, UUID(user_sub))
            idc = requested_claims["id_token"]
            if "email" in idc:
                extra_claims["email"] = user_obj.email if user_obj else ""
            if any(k in idc for k in ("name", "preferred_username")):
                extra_claims["name"] = session.get("username")
        if access:
            extra_claims["at_hash"] = oidc_hash(access)
        if code:
            extra_claims["c_hash"] = oidc_hash(str(code))
        id_token = await mint_id_token(
            sub=user_sub,
            aud=client_id,
            nonce=nonce,
            issuer=ISSUER,
            **extra_claims,
        )
        params.append(("id_token", id_token))
    if state:
        params.append(("state", state))
    if mode == "fragment":
        redirect_url = f"{redirect_uri}#{urlencode(params)}" if params else redirect_uri
        return RedirectResponse(redirect_url)
    if mode == "form_post":
        inputs = "".join(
            f'<input type="hidden" name="{k}" value="{v}" />' for k, v in params
        )
        body = (
            "<!DOCTYPE html><html><body>"
            f'<form method="post" action="{redirect_uri}">{inputs}</form>'
            "<script>document.forms[0].submit()</script>"
            "</body></html>"
        )
        return HTMLResponse(content=body)
    redirect_url = f"{redirect_uri}?{urlencode(params)}" if params else redirect_uri
    return RedirectResponse(redirect_url)
