from __future__ import annotations

from .. import log, rpc
from peagen.defaults import SECRETS_ADD, SECRETS_GET, SECRETS_DELETE
from ..db_helpers import delete_secret, fetch_secret, upsert_secret
from peagen.defaults.error_codes import ErrorCode
from peagen.transport.jsonrpc import RPCException


@rpc.method(SECRETS_ADD)
async def secrets_add(
    name: str,
    secret: str,
    tenant_id: str = "default",
    owner_fpr: str = "unknown",
    version: int | None = None,
) -> dict:
    """Store an encrypted secret."""
    from peagen.gateway import db

    async with db.Session() as session:
        await upsert_secret(session, tenant_id, owner_fpr, name, secret)
        await session.commit()
    log.info("secret stored: %s", name)
    return {"ok": True}


@rpc.method(SECRETS_GET)
async def secrets_get(name: str, tenant_id: str = "default") -> dict:
    """Retrieve an encrypted secret."""
    from peagen.gateway import db

    async with db.Session() as session:
        row = await fetch_secret(session, tenant_id, name)
    if not row:
        raise RPCException(
            code=ErrorCode.SECRET_NOT_FOUND,
            message="secret not found",
        )
    return {"secret": row.cipher}


@rpc.method(SECRETS_DELETE)
async def secrets_delete(
    name: str,
    tenant_id: str = "default",
    version: int | None = None,
) -> dict:
    """Remove a secret by name."""
    from peagen.gateway import db

    async with db.Session() as session:
        await delete_secret(session, tenant_id, name)
        await session.commit()
    log.info("secret removed: %s", name)
    return {"ok": True}
