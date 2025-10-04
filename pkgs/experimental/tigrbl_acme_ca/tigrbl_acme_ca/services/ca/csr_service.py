from __future__ import annotations

import base64

def b64url_to_bytes(data: str) -> bytes:
    pad = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)
