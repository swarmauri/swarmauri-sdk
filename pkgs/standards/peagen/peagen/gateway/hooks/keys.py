"""
gateway.hooks.keys
──────────────────────
AutoAPI-native JSON-RPC hooks for trusted-public-key management.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict

from autoapi.v2 import AutoAPI, Phase
from pgpy import PGPKey

from peagen.orm import DeployKey

from peagen.gateway import api, log

# -------------------------------------------------------------------
# Resolve the exact server-side schemas once (lru_cached inside AutoAPI)
SCreate = AutoAPI.get_schema(DeployKey, "create")  # body for DeployKey.create
SRead = AutoAPI.get_schema(DeployKey, "read")  # single-row read
SDelete = AutoAPI.get_schema(DeployKey, "delete")  # pk-only schema
SListIn = AutoAPI.get_schema(DeployKey, "list")  # fetch all keys
# -------------------------------------------------------------------


@api.hook(Phase.PRE_TX_BEGIN, model="DeployKey", op="create")
async def pre_key_upload(ctx: Dict[str, Any]) -> None:
    """Validate the uploaded key and prepare DB row."""
    log.info("entering pre_key_upload")

    try:
        params: SCreate = ctx["env"].params  # ← validated by AutoAPI
        pgp = PGPKey()
        pgp.parse(params.public_key)

        ctx["key_data"] = {
            "id": str(uuid.uuid4()),
            "user_id": None,  # resolved by service layer
            "name": f"{pgp.fingerprint[:16]}-key",
            "public_key": params.public_key,
            "secret_id": None,
            "read_only": True,
        }
        ctx["fingerprint"] = pgp.fingerprint
    except Exception as exc:
        raise exc


@api.hook(Phase.POST_COMMIT, model="DeployKey", op="create")
async def post_key_upload(ctx: Dict[str, Any]) -> None:
    """Cache the key in memory and shape the RPC result."""
    log.info("entering post_key_upload")

    params: SCreate = ctx["env"].params
    fp: str = params.fingerprint

    log.info("key persisted (fingerprint=%s)", fp)


@api.hook(Phase.POST_HANDLER, model="DeployKey", op="read")
async def post_key_fetch(ctx: Dict[str, Any]) -> None:
    """Convert the raw DB rows into a {fingerprint: key} mapping."""
    log.info("entering POST_HANDLER")

    # rows = ctx.get("result", [])
    # mapping: Dict[str, str] = {}

    # for row in rows:
    #     pub = row["public_key"] if isinstance(row, dict) else row.public_key
    #     pgp = PGPKey()
    #     pgp.parse(pub)
    #     mapping[pgp.fingerprint] = pub

    # ctx["result"] = {"keys": mapping}  # simple dict for clients


@api.hook(Phase.PRE_TX_BEGIN, model="DeployKey", op="delete")
async def pre_key_delete(ctx: Dict[str, Any]) -> None:
    """Extract the fingerprint so the post-hook can update the cache."""
    log.info("entering pre_key_delete")

    params: SDelete = ctx["env"].params
    ctx["fingerprint"] = params.fingerprint


@api.hook(Phase.POST_COMMIT, model="DeployKey", op="delete")
async def post_key_delete(ctx: Dict[str, Any]) -> None:
    """Purge the key from memory and return an OK payload."""
    log.info("entering post_key_delete")

    fp = ctx["fingerprint"]
    log.info("key removed: %s", fp)
