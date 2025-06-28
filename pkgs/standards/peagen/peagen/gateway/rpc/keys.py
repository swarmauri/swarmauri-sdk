from __future__ import annotations

from pgpy import PGPKey

from .. import dispatcher, log, TRUSTED_USERS
from peagen.defaults import KEYS_UPLOAD, KEYS_FETCH, KEYS_DELETE
from peagen.rpc_models import (
    KeysUploadParams,
    KeysUploadResult,
    KeysFetchResult,
    KeysDeleteParams,
    KeysDeleteResult,
)


@dispatcher.method(KEYS_UPLOAD)
async def keys_upload(public_key: str) -> dict:
    """Store a trusted public key."""
    params = KeysUploadParams(public_key=public_key)
    key = PGPKey()
    key.parse(params.public_key)
    TRUSTED_USERS[key.fingerprint] = params.public_key
    log.info("key uploaded: %s", key.fingerprint)
    result = KeysUploadResult(fingerprint=key.fingerprint)
    return result.model_dump()


@dispatcher.method(KEYS_FETCH)
async def keys_fetch() -> dict:
    """Return all trusted keys indexed by fingerprint."""
    result = KeysFetchResult(keys=TRUSTED_USERS)
    return result.model_dump()


@dispatcher.method(KEYS_DELETE)
async def keys_delete(fingerprint: str) -> dict:
    """Remove a public key by its fingerprint."""
    params = KeysDeleteParams(fingerprint=fingerprint)
    TRUSTED_USERS.pop(params.fingerprint, None)
    log.info("key removed: %s", params.fingerprint)
    result = KeysDeleteResult(ok=True)
    return result.model_dump()
