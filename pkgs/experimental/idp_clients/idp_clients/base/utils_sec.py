from __future__ import annotations
import base64, hashlib, hmac, json, os, time
from typing import Dict, Any, Tuple

def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")

def make_pkce_pair() -> Tuple[str, str]:
    verifier = b64u(os.urandom(32))  # 43–128 chars after base64url
    challenge = b64u(hashlib.sha256(verifier.encode()).digest())
    return verifier, challenge

def make_nonce() -> str:
    return b64u(os.urandom(16))

def sign_state(secret: bytes, payload: Dict[str, Any], ttl_sec: int = 600) -> str:
    body = b64u(json.dumps({**payload, "exp": int(time.time()) + ttl_sec}).encode())
    mac  = b64u(hmac.new(secret, body.encode(), hashlib.sha256).digest())
    return f"{body}.{mac}"

def verify_state(secret: bytes, state: str) -> Dict[str, Any]:
    body, mac = state.split(".", 1)
    expected = b64u(hmac.new(secret, body.encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(mac, expected):
        raise ValueError("bad-mac")
    payload = json.loads(base64.urlsafe_b64decode(body + "=="))
    if payload.get("exp", 0) < time.time():
        raise ValueError("expired")
    return payload
