"""
AutoAPI hooks for key-related operations.
"""

import uuid
from typing import Any, Dict

from pgpy import PGPKey
from sqlalchemy import select

from peagen.orm.repo.deploy_key import DeployKeyModel

from ... import log
from ...autoapi import api

# ---------------------- Keys Hooks ----------------------


@api.hook(api.Phase.PRE_TX_BEGIN, method="deploy_keys.create")
async def pre_key_create(ctx: Dict[str, Any]) -> None:
    """Pre-processing for key upload (previously keys_upload)"""
    params = ctx.get("env").params

    # Parse PGP key to get fingerprint
    pgp = PGPKey()
    pgp.parse(params.get("public_key", ""))
    fingerprint = pgp.fingerprint

    # Generate a UUID for the key
    key_id = str(uuid.uuid4())

    # Store for later use
    ctx["fingerprint"] = fingerprint
    ctx["key_id"] = key_id

    # Update params with fields expected by the ORM model
    params["id"] = key_id
    params["name"] = f"{fingerprint[:16]}-key"
    params["user_id"] = params.get("user_id") or None  # server will resolve to caller
    params["secret_id"] = None
    params["read_only"] = True


@api.hook(api.Phase.POST_HANDLER, method="deploy_keys.create")
async def post_key_create_handler(ctx: Dict[str, Any]) -> None:
    """Handle potential duplicate keys"""
    result = ctx.get("result")
    params = ctx.get("env").params

    if not result:
        # Check if key already exists (handle idempotency)
        db = next(ctx.get("db_ctx").db())
        stmt = select(DeployKeyModel).where(
            DeployKeyModel.public_key == params.get("public_key")
        )
        existing_key = db.execute(stmt).first()

        if existing_key:
            # Key already exists, use it as the result
            ctx["result"] = {
                "id": str(existing_key[0].id),
                "name": existing_key[0].name,
                "public_key": existing_key[0].public_key,
            }


@api.hook(api.Phase.POST_COMMIT, method="deploy_keys.create")
async def post_key_create(ctx: Dict[str, Any]) -> None:
    """Post-commit operations for key upload"""
    result = ctx.get("result")
    fingerprint = ctx.get("fingerprint")

    if result and "public_key" in result:
        # Update TRUSTED_USERS dictionary as in original implementation
        from ... import TRUSTED_USERS

        TRUSTED_USERS[fingerprint] = result["public_key"]
        log.info("key persisted (fingerprint = %s)", fingerprint)

        # Format response to match original API
        ctx["result"] = {"fingerprint": fingerprint}


@api.hook(api.Phase.POST_HANDLER, method="deploy_keys.list")
async def post_key_list(ctx: Dict[str, Any]) -> None:
    """Post-handler operations for key listing"""
    result = ctx.get("result")

    if not result:
        ctx["result"] = {"keys": {}}
        return

    # Convert list of keys to fingerprint -> public_key mapping
    from ... import TRUSTED_USERS

    mapping = {}
    for key in result:
        if "public_key" in key:
            pgp = PGPKey()
            pgp.parse(key["public_key"])
            fingerprint = pgp.fingerprint
            mapping[fingerprint] = key["public_key"]

    # Update TRUSTED_USERS as in original implementation
    TRUSTED_USERS.clear()
    TRUSTED_USERS.update(mapping)

    # Format response to match original API
    ctx["result"] = {"keys": mapping}


@api.hook(api.Phase.PRE_TX_BEGIN, method="deploy_keys.delete")
async def pre_key_delete(ctx: Dict[str, Any]) -> None:
    """Pre-processing for key deletion"""
    params = ctx.get("env").params
    fingerprint = params.get("fingerprint")

    if not fingerprint:
        return

    # Store for later
    ctx["fingerprint"] = fingerprint

    # Need to find the key by fingerprint rather than ID
    db = next(ctx.get("db_ctx").db())
    keys = db.execute(select(DeployKeyModel)).all()

    for key_row in keys:
        key = key_row[0]
        pgp = PGPKey()
        try:
            pgp.parse(key.public_key)
            if pgp.fingerprint == fingerprint:
                # Found the key, set the ID for deletion
                params["id"] = str(key.id)
                ctx["key_found"] = True
                break
        except Exception:
            continue

    if not ctx.get("key_found"):
        raise ValueError(f"fingerprint {fingerprint} not found")


@api.hook(api.Phase.POST_COMMIT, method="deploy_keys.delete")
async def post_key_delete(ctx: Dict[str, Any]) -> None:
    """Post-commit operations for key deletion"""
    result = ctx.get("result")
    fingerprint = ctx.get("fingerprint")

    if result and fingerprint:
        from ... import TRUSTED_USERS

        if fingerprint in TRUSTED_USERS:
            del TRUSTED_USERS[fingerprint]

        # Format response to match original API
        ctx["result"] = {"ok": True}

        # Log deletion
        log.info("key deleted (fingerprint = %s)", fingerprint)
