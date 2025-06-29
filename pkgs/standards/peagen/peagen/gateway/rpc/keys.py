from __future__ import annotations

from pgpy import PGPKey

from .. import dispatcher, log, TRUSTED_USERS
from peagen.transport.json_rpcschemas.keys import (
    KEYS_UPLOAD,
    KEYS_FETCH,
    KEYS_DELETE,
    UploadParams,
    UploadResult,
    FetchResult,
    DeleteParams,
    DeleteResult,
)


@dispatcher.method(KEYS_UPLOAD)
async def keys_upload(params: UploadParams) -> dict:
    """Store a trusted public key."""
    key = PGPKey()
    key.parse(params.public_key)
    TRUSTED_USERS[key.fingerprint] = params.public_key
    log.info("key uploaded: %s", key.fingerprint)
    return UploadResult(fingerprint=key.fingerprint).model_dump()


@dispatcher.method(KEYS_FETCH)
async def keys_fetch() -> dict:
    """Return all trusted keys indexed by fingerprint."""
    return FetchResult(keys=TRUSTED_USERS).model_dump()


@dispatcher.method(KEYS_DELETE)
async def keys_delete(params: DeleteParams) -> dict:
    """Remove a public key by its fingerprint."""
    TRUSTED_USERS.pop(params.fingerprint, None)
    log.info("key removed: %s", params.fingerprint)
    return DeleteResult(ok=True).model_dump()
