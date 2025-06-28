from __future__ import annotations

from .. import log, rpc, Session
from ..db_helpers import delete_secret, fetch_secret, upsert_secret
from peagen.gateway.errors import GatewayError, raise_rpc


@rpc.method("Secrets.add")
async def secrets_add(
    name: str,
    secret: str,
    tenant_id: str = "default",
    owner_fpr: str = "unknown",
    version: int | None = None,
) -> dict:
    """Store an encrypted secret."""
    async with Session() as session:
        await upsert_secret(session, tenant_id, owner_fpr, name, secret)
        await session.commit()
    log.info("secret stored: %s", name)
    return {"ok": True}


@rpc.method("Secrets.get")
async def secrets_get(name: str, tenant_id: str = "default") -> dict:
    """Retrieve an encrypted secret."""
    async with Session() as session:
        row = await fetch_secret(session, tenant_id, name)
    if not row:
        raise_rpc(GatewayError.INVALID_PARAMS, "secret not found")
    return {"secret": row.cipher}


@rpc.method("Secrets.delete")
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
