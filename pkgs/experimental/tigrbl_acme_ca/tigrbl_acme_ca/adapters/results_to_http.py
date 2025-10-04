from __future__ import annotations

from typing import Dict, Tuple, List, Any

def _get_accept(ctx) -> str:
    hdrs = ctx.get("request_headers") or {}
    return (hdrs.get("accept") or hdrs.get("Accept") or "*/*")

def attach_replay_nonce(ctx, value: str) -> None:
    try:
        headers = ctx.response_headers()
        headers["Replay-Nonce"] = value
    except Exception:
        pass

def negotiate_cert_response(ctx, pem: str, chain: List[str] | None = None) -> Tuple[int, Dict[str, str], bytes]:
    """Negotiate certificate download format based on Accept header.
    application/pem-certificate-chain: full chain as concatenated PEMs
    application/pem-certificate: leaf only
    */*: default to leaf only
    Returns: (status_code, headers, body_bytes)
    """
    accept = _get_accept(ctx).lower()
    headers: Dict[str, str] = {}
    if "application/pem-certificate-chain" in accept and chain:
        body = ("\n".join(chain)).encode("utf-8")
        headers["Content-Type"] = "application/pem-certificate-chain"
        return 200, headers, body
    # default: leaf certificate
    body = pem.encode("utf-8")
    headers["Content-Type"] = "application/pem-certificate"
    return 200, headers, body
