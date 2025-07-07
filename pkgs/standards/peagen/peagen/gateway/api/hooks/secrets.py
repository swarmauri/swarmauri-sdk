from __future__ import annotations

from typing import Any, Dict

from autoapi.v2 import Phase

from peagen.transport.error_codes import ErrorCode
from peagen.transport.jsonrpc import RPCException
from peagen.transport.jsonrpc_schemas.secrets import (
    AddResult,
    DeleteResult,
    GetResult,
)

from .. import log
from . import api

# ------------------------------------------------------------------------
# Secret model hooks
# ------------------------------------------------------------------------


@api.hook(Phase.POST_COMMIT, method="secrets.create")
async def post_secret_add(ctx: Dict[str, Any]) -> None:
    """Post-hook for secret creation: Additional actions after persistence."""
    params = ctx["env"].params

    # AutoAPI has already stored the secret, just log and perform any additional actions
    log.info("Secret stored successfully: %s", params.name)

    # If you need to customize the response format
    ctx["result"] = AddResult(ok=True).model_dump()


@api.hook(Phase.POST_HANDLER, method="secrets.read")
async def post_secret_get(ctx: Dict[str, Any]) -> None:
    """Post-hook for secret retrieval: Transform the result."""
    result = ctx.get("result")

    if not result or "cipher" not in result:
        raise RPCException(
            code=ErrorCode.SECRET_NOT_FOUND,
            message="Secret not found or missing cipher data",
        )

    # Transform the AutoAPI result into the expected response format
    ctx["result"] = GetResult(secret=result["cipher"]).model_dump()


@api.hook(Phase.POST_COMMIT, method="secrets.delete")
async def post_secret_delete(ctx: Dict[str, Any]) -> None:
    """Post-hook for secret deletion: Actions after deletion."""
    params = ctx["env"].params

    # AutoAPI has already deleted the secret, just log and do any cleanup
    log.info("Secret deleted: %s", params.name)

    # Set the response format
    ctx["result"] = DeleteResult(ok=True).model_dump()
