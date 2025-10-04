from __future__ import annotations
from pydantic import BaseModel, Field

class FinalizeCSR(BaseModel):
    csr: str = Field(..., description="base64url DER PKCS#10 CSR")

def b64url_to_bytes(data: str) -> bytes:
    import base64
    pad = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)
