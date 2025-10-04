from __future__ import annotations

REDACT_KEYS = {
    "csr", "csr_der_b64", "pem", "private_key", "hmac_key_b64", "token"
}

def redact_payload(payload: dict | None) -> dict:
    if not isinstance(payload, dict):
        return {}
    redacted = {}
    for k, v in payload.items():
        if k in REDACT_KEYS:
            redacted[k] = "***redacted***"
        else:
            redacted[k] = v
    return redacted
