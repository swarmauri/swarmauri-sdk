from __future__ import annotations
from fastapi import HTTPException
import json, base64

def _b64url_to_json(data: str) -> dict:
    pad = '=' * (-len(data) % 4)
    raw = base64.urlsafe_b64decode(data + pad)
    return json.loads(raw.decode('utf-8'))

async def require_jws(ctx) -> None:
    jws = ctx.get("jws")
    if not isinstance(jws, dict):
        raise HTTPException(status_code=400, detail="malformed_jws")
    protected = jws.get("protected")
    payload = jws.get("payload")
    signature = jws.get("signature")
    if not (protected and payload and signature):
        raise HTTPException(status_code=400, detail="malformed_jws")
    try:
        header = _b64url_to_json(protected)
    except Exception:
        raise HTTPException(status_code=400, detail="bad_protected_header")
    # Stash convenience fields for downstream ops/hooks
    ctx.setdefault("jws_header", header)
    ctx.setdefault("jws_payload_b64", payload)
    # Nonce is in the protected header per RFC8555
    nonce = header.get("nonce")
    if not nonce:
        raise HTTPException(status_code=400, detail="badNonce")
    ctx["request_nonce"] = nonce
