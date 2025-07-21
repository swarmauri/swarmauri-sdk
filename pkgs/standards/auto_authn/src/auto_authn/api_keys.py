"""
auth_authn_idp.api_keys
~~~~~~~~~~~~~~~~~~~~~~~
Business logic for Personal‑Access‑Tokens (“API keys”).

Key features
------------
• Opaque secrets – shown **once** at creation, never persisted in plaintext.  
• Tenant isolation – every query is scoped by ``tenant_id``.  
• Config‑driven TTL limits (``API_KEY_MIN_TTL`` / ``API_KEY_MAX_TTL``).  
• Revocation & rotation support.  
"""

from __future__ import annotations

import datetime as dt
import hashlib
import secrets
from typing import Iterable, Sequence
from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .config import API_KEY_HASH_SECRET, API_KEY_MAX_TTL, API_KEY_MIN_TTL
from .models import APIKey

__all__ = [
    "create_api_key",
    "verify_api_key",
    "revoke_api_key",
]

# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #
def _hash(secret: str) -> str:
    """
    Server‑side hashing (pepper + SHA‑256) – prevents rainbow‑table attacks
    even if the DB leaks.
    """
    return hashlib.sha256(f"{API_KEY_HASH_SECRET}{secret}".encode()).hexdigest()


# --------------------------------------------------------------------------- #
# CRUD                                                                        #
# --------------------------------------------------------------------------- #
async def create_api_key(
    db: AsyncSession,
    *,
    tenant_id: int,
    owner_id: UUID,
    scopes: Sequence[str],
    ttl_days: int = 30,
    label: str | None = None,
) -> str:
    """
    Mint a new API key bound to ``owner_id`` and ``tenant_id``.

    Returns
    -------
    str
        **Plaintext secret** – *display / return this exactly once*.
    """
    if not API_KEY_MIN_TTL <= ttl_days <= API_KEY_MAX_TTL:
        raise ValueError(
            f"TTL must be between {API_KEY_MIN_TTL}–{API_KEY_MAX_TTL} days"
        )

    raw_secret = secrets.token_urlsafe(32)  # 43‑44 chars, URL‑safe
    expires = dt.datetime.utcnow() + dt.timedelta(days=ttl_days)

    rec = APIKey(
        id=uuid4(),
        tenant_id=tenant_id,
        owner_id=owner_id,
        label=label,
        prefix=raw_secret[:8],
        hashed_key=_hash(raw_secret),
        scopes=list(scopes),
        expires_at=expires,
    )
    db.add(rec)
    await db.commit()
    return raw_secret


async def verify_api_key(
    raw_secret: str,
    db: AsyncSession,
    tenant_id: int,
) -> APIKey | None:
    """
    Validate an incoming API‑key *secret* and return its DB record on success.

    Notes
    -----
    • Performs constant‑time comparison to prevent timing attacks.  
    • Rejects expired or revoked keys.  
    """
    if len(raw_secret) < 8:
        return None

    stmt = (
        select(APIKey)
        .where(APIKey.tenant_id == tenant_id)
        .where(APIKey.prefix == raw_secret[:8])
        .where(APIKey.revoked_at.is_(None))
        .limit(1)
    )
    rec: APIKey | None = (await db.scalars(stmt)).one_or_none()
    if not rec:
        return None

    now = dt.datetime.utcnow()
    if rec.expires_at <= now:
        return None

    if secrets.compare_digest(rec.hashed_key, _hash(raw_secret)):
        return rec
    return None


async def revoke_api_key(
    db: AsyncSession,
    *,
    tenant_id: int,
    api_key_id: UUID,
) -> bool:
    """
    Set ``revoked_at`` on the specified key.

    Returns
    -------
    bool
        ``True`` if a key was found & revoked, ``False`` otherwise.
    """
    result = await db.execute(
        update(APIKey)
        .where(APIKey.id == api_key_id, APIKey.tenant_id == tenant_id)
        .where(APIKey.revoked_at.is_(None))
        .values(revoked_at=dt.datetime.utcnow())
        .execution_options(synchronize_session="fetch")
    )
    await db.commit()
    return result.rowcount == 1
