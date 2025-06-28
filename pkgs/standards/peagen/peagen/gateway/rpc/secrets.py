from __future__ import annotations

from .. import Session, dispatcher, log
from peagen.protocols.methods.secrets import (
    SECRETS_ADD,
    SECRETS_GET,
    SECRETS_DELETE,
    AddParams,
    AddResult,
    GetParams,
    GetResult,
    DeleteParams,
    DeleteResult,
)
from ..db_helpers import delete_secret, fetch_secret, upsert_secret
from peagen.protocols.error_codes import Code as ErrorCode
from peagen.transport.jsonrpc import RPCException


@dispatcher.method(SECRETS_ADD)
async def secrets_add(params: AddParams) -> dict:
    """Store an encrypted secret."""
    async with Session() as session:
        await upsert_secret(
            session,
            params.tenant_id,
            params.owner_user_id or "unknown",
            params.name,
            params.cipher,
        )
        await session.commit()
    log.info("secret stored: %s", params.name)
    return AddResult(ok=True).model_dump()


@dispatcher.method(SECRETS_GET)
async def secrets_get(params: GetParams) -> dict:
    """Retrieve an encrypted secret."""
    async with Session() as session:
        row = await fetch_secret(session, params.tenant_id, params.name)
    if not row:
        raise RPCException(
            code=ErrorCode.SECRET_NOT_FOUND,
            message="secret not found",
        )
    return GetResult(secret=row.cipher).model_dump()


@dispatcher.method(SECRETS_DELETE)
async def secrets_delete(params: DeleteParams) -> dict:
    """Remove a secret by name."""
    async with Session() as session:
        await delete_secret(session, params.tenant_id, params.name)
        await session.commit()
    log.info("secret removed: %s", params.name)
    return DeleteResult(ok=True).model_dump()
