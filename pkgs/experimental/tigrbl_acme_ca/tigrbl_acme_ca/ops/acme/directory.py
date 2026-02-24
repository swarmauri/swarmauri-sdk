from __future__ import annotations
from typing import Dict


async def directory(ctx) -> Dict[str, object]:
    base_url = ctx.get("base_url") or ""
    if base_url.endswith("/"):
        base_url = base_url[:-1]
    return {
        "newNonce": f"{base_url}/acme/new-nonce",
        "newAccount": f"{base_url}/acme/new-account",
        "newOrder": f"{base_url}/acme/new-order",
        "revokeCert": f"{base_url}/acme/revoke-cert",
        "keyChange": f"{base_url}/acme/key-change",
        "meta": {
            "termsOfService": f"{base_url}/tos",
            "website": f"{base_url}/",
            "caaIdentities": ["tigrbl-acme-ca"],
            "externalAccountRequired": False,
        },
    }
