from __future__ import annotations

from .. import Session, dispatcher, log
from peagen.defaults import SECRETS_ADD, SECRETS_GET, SECRETS_DELETE
from ..db_helpers import delete_secret, fetch_secret, upsert_secret
from peagen.protocols.error_codes import Code as ErrorCode
from peagen.transport.jsonrpc import RPCException


@dispatcher.method(SECRETS_ADD)
async def secrets_add(
    name: str,
    cipher: str,
    tenant_id: str = "default",
    owner_user_id: str | None = None,
    version: int | None = None,
) -> dict:
    """Store an encrypted secret."""
    async with Session() as session:
        await upsert_secret(session, tenant_id, "unknown", name, cipher)
        await session.commit()
    log.info("secret stored: %s", name)
    return {"ok": True}


@dispatcher.method(SECRETS_GET)
async def secrets_get(name: str, tenant_id: str = "default") -> dict:
    """Retrieve an encrypted secret."""
    async with Session() as session:
        row = await fetch_secret(session, tenant_id, name)
    if not row:
        raise RPCException(
            code=ErrorCode.SECRET_NOT_FOUND,
            message="secret not found",
        )
    return {"secret": row.cipher}


@dispatcher.method(SECRETS_DELETE)
async def secrets_delete(
    name: str,
    tenant_id: str = "default",
    version: int | None = None,
) -> dict:
    """Remove a secret by name."""
    async with Session() as session:
        await delete_secret(session, tenant_id, name)
        await session.commit()
    log.info("secret removed: %s", name)
    return {"ok": True}
