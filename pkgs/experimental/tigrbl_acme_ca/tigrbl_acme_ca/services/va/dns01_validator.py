from __future__ import annotations
import base64
import hashlib
from typing import Iterable


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


async def validate_dns01(ctx, domain: str, token: str, jwk_thumbprint: str) -> bool:
    resolver = ctx.get("dns_resolver")
    if resolver is None:
        # Expect the runtime to inject a resolver with .txt_lookup()
        raise RuntimeError("dns_resolver not available in ctx")
    key_auth = f"{token}.{jwk_thumbprint}".encode("utf-8")
    digest = hashlib.sha256(key_auth).digest()
    expected = b64url(digest)
    name = f"_acme-challenge.{domain.rstrip('.')}"
    answers: Iterable[str] = await resolver.txt_lookup(name)
    candidates = {a.strip().strip('"') for a in (answers or [])}
    return expected in candidates
