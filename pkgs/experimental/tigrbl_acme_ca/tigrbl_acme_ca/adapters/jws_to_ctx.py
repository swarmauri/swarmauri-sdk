from __future__ import annotations

import base64, json, hashlib
from typing import Any, Dict, Optional

def _b64url_to_bytes(data: str) -> bytes:
    pad = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

def _canonical_json(obj: Dict[str, Any]) -> bytes:
    # RFC 7638: lexicographic, separators without spaces, ensure_ascii True
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")

def jwk_thumbprint(jwk: Dict[str, Any]) -> str:
    """Compute RFC 7638 JWK thumbprint (SHA-256 of canonical JSON).
    Supports RSA (kty/e/n) and EC (kty/crv/x/y).
    """
    kty = jwk.get("kty")
    if kty == "RSA":
        material = {"e": jwk["e"], "kty": "RSA", "n": jwk["n"]}
    elif kty == "EC":
        material = {"crv": jwk["crv"], "kty": "EC", "x": jwk["x"], "y": jwk["y"]}
    else:
        raise ValueError("unsupported_jwk_kty")
    digest = hashlib.sha256(_canonical_json(material)).digest()
    return _b64url(digest)

def parse_acme_jws_from_body(body: bytes) -> Dict[str, Any]:
    """Parse an ACME JWS object (JSON with base64url fields) from HTTP body.
    Returns a dict with keys: protected (str), payload (str), signature (str), header (dict).
    This function DOES NOT verify signatures; guards/engines should perform that step if needed.
    """
    try:
        obj = json.loads(body.decode("utf-8"))
        protected = obj.get("protected"); payload = obj.get("payload"); signature = obj.get("signature")
        if not (isinstance(protected, str) and isinstance(payload, str) and isinstance(signature, str)):
            raise ValueError("malformed_jws")
        header_raw = _b64url_to_bytes(protected)
        header = json.loads(header_raw.decode("utf-8"))
        obj["header"] = header
        return obj
    except Exception as e:
        raise ValueError(f"malformed_jws:{e}")

def populate_ctx_from_jws(ctx: Dict[str, Any], jws: Dict[str, Any]) -> None:
    """Populate the Tigrbl request ctx with ACME JWS fields.
    - ctx['jws'] original object
    - ctx['jws_header'] parsed protected header
    - ctx['jws_payload_b64'] base64url payload (do not decode here)
    - ctx['request_nonce'] from protected header 'nonce'
    - ctx['account_kid'] from protected header 'kid' (if present)
    - ctx['account_jwk'] from protected header 'jwk' (if present)
    - ctx['request_url'] from protected header 'url' (if present)
    - ctx['actor_account_thumbprint'] optional computed from jwk
    """
    header = jws.get("header") or {}
    ctx["jws"] = jws
    ctx["jws_header"] = header
    ctx["jws_payload_b64"] = jws.get("payload")
    nonce = header.get("nonce")
    if nonce:
        ctx["request_nonce"] = nonce
    kid = header.get("kid")
    jwk = header.get("jwk")
    if kid:
        ctx["account_kid"] = kid
    if jwk:
        ctx["account_jwk"] = jwk
        try:
            ctx["actor_account_thumbprint"] = jwk_thumbprint(jwk)
        except Exception:
            # ignore if unsupported/invalid
            pass
    url = header.get("url")
    if url:
        ctx["request_url"] = url
