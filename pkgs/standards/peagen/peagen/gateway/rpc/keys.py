"""
peagen.gateway.rpc.keys
-----------------------

JSON-RPC interface for managing trusted public keys.

Public contract (unchanged)
~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Params  : UploadParams · FetchParams · DeleteParams
* Results : UploadResult · FetchResult · DeleteResult
"""

from __future__ import annotations

import uuid
from typing import Any, Dict

from autoapi.v2 import Phase
from pgpy import PGPKey

from peagen.transport.jsonrpc_schemas.keys import (
    DeleteResult,
    FetchResult,
    UploadResult,
)

from .. import TRUSTED_USERS, log
from . import api

# ------------------------------------------------------------------------
# Key operation hooks
# ------------------------------------------------------------------------


@api.hook(Phase.PRE_TX_BEGIN, method="deploy_keys.create")
async def pre_key_upload(ctx: Dict[str, Any]) -> None:
    """Pre-hook for key upload: Parse key and prepare data for persistence."""
    params = ctx["env"].params

    # Parse the key to validate and get fingerprint
    pgp = PGPKey()
    pgp.parse(params.public_key)

    # Prepare data for database
    ctx["key_data"] = {
        "id": str(uuid.uuid4()),
        "user_id": None,  # server will resolve to caller
        "name": f"{pgp.fingerprint[:16]}-key",
        "public_key": params.public_key,
        "secret_id": None,
        "read_only": True,
    }
    ctx["fingerprint"] = pgp.fingerprint


@api.hook(Phase.POST_COMMIT, method="deploy_keys.create")
async def post_key_upload(ctx: Dict[str, Any]) -> None:
    """Post-hook for key upload: Store in memory cache and format response."""
    params = ctx["env"].params
    fingerprint = ctx["fingerprint"]

    # Store in memory
    TRUSTED_USERS[fingerprint] = params.public_key

    log.info("key persisted (fingerprint = %s)", fingerprint)

    # Set response format
    ctx["result"] = UploadResult(fingerprint=fingerprint).model_dump()


@api.hook(Phase.POST_HANDLER, method="deploy_keys.read")
async def post_key_fetch(ctx: Dict[str, Any]) -> None:
    """Post-hook for key fetch: Format keys into response."""
    # Get keys from database result
    raw = ctx.get("result", [])

    # Convert to fingerprint mapping
    mapping = {
        PGPKey().parse(row["public_key"]).fingerprint: row["public_key"] for row in raw
    }

    # Update memory cache
    TRUSTED_USERS.clear()
    TRUSTED_USERS.update(mapping)

    # Set response format
    ctx["result"] = FetchResult(keys=mapping).model_dump()


@api.hook(Phase.PRE_TX_BEGIN, method="deploy_keys.delete")
async def pre_key_delete(ctx: Dict[str, Any]) -> None:
    """Pre-hook for key deletion: Find the key by fingerprint."""
    params = ctx["env"].params
    fingerprint = params.fingerprint

    # We need to find the key ID from the fingerprint
    # This will be used for database operations
    # Store fingerprint for post-hook
    ctx["fingerprint"] = fingerprint


@api.hook(Phase.POST_COMMIT, method="deploy_keys.delete")
async def post_key_delete(ctx: Dict[str, Any]) -> None:
    """Post-hook for key deletion: Remove from memory and format response."""
    fingerprint = ctx["fingerprint"]

    # Remove from memory
    TRUSTED_USERS.pop(fingerprint, None)

    log.info("key removed: %s", fingerprint)

    # Set response format
    ctx["result"] = DeleteResult(ok=True).model_dump()
