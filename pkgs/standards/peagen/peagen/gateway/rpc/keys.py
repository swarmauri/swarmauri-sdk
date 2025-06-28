from __future__ import annotations

from pgpy import PGPKey

from .. import log, rpc, TRUSTED_USERS


@rpc.method("Keys.upload")
async def keys_upload(public_key: str) -> dict:
    """Store a trusted public key."""
    key = PGPKey()
    key.parse(public_key)
    TRUSTED_USERS[key.fingerprint] = public_key
    log.info("key uploaded: %s", key.fingerprint)
    return {"fingerprint": key.fingerprint}


@rpc.method("Keys.fetch")
async def keys_fetch() -> dict:
    """Return all trusted keys indexed by fingerprint."""
    return TRUSTED_USERS


@rpc.method("Keys.delete")
async def keys_delete(fingerprint: str) -> dict:
    """Remove a public key by its fingerprint."""
    TRUSTED_USERS.pop(fingerprint, None)
    log.info("key removed: %s", fingerprint)
    return {"ok": True}
