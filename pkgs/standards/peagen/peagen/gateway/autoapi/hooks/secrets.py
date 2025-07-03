"""
AutoAPI hooks for secrets-related operations.
"""

from typing import Any, Dict

from peagen.transport.error_codes import ErrorCode
from peagen.transport.jsonrpc import RPCException

from ... import log
from ...autoapi import api

# ---------------------- Secrets Hooks ----------------------


@api.hook(api.Phase.PRE_TX_BEGIN, method="secrets.create")
async def pre_secret_create(ctx: Dict[str, Any]) -> None:
    """Pre-processing for secret creation"""
    params = ctx.get("env").params

    # Ensure owner_user_id has a default value as in the original implementation
    if not params.get("owner_user_id"):
        params["owner_user_id"] = "unknown"

    # Store original params for logging
    ctx["secret_name"] = params.get("name")


@api.hook(api.Phase.POST_COMMIT, method="secrets.create")
async def post_secret_create(ctx: Dict[str, Any]) -> None:
    """Post-commit operations for secret creation"""
    secret_name = ctx.get("secret_name")
    if secret_name:
        log.info("secret stored: %s", secret_name)


@api.hook(api.Phase.POST_HANDLER, method="secrets.read")
async def post_secret_read(ctx: Dict[str, Any]) -> None:
    """Post-handler operations for secret retrieval"""
    result = ctx.get("result")

    # If no result found, raise the same exception as in the original implementation
    if not result:
        raise RPCException(
            code=ErrorCode.SECRET_NOT_FOUND,
            message="secret not found",
        )

    # AutoAPI returns the full model, but original API returns just the cipher
    if "cipher" in result:
        # Keep the original response structure
        ctx["result"] = {"secret": result["cipher"]}


@api.hook(api.Phase.PRE_TX_BEGIN, method="secrets.delete")
async def pre_secret_delete(ctx: Dict[str, Any]) -> None:
    """Pre-processing for secret deletion"""
    params = ctx.get("env").params

    # Store for logging
    ctx["secret_name"] = params.get("name")


@api.hook(api.Phase.POST_COMMIT, method="secrets.delete")
async def post_secret_delete(ctx: Dict[str, Any]) -> None:
    """Post-commit operations for secret deletion"""
    secret_name = ctx.get("secret_name")
    if secret_name:
        log.info("secret removed: %s", secret_name)
