from __future__ import annotations

import secrets, hmac, hashlib
from datetime import datetime, timezone
from uuid import UUID

from ..types import (
    Column, String, Boolean, DateTime, ForeignKey, Index,
    LargeBinary, relationship, UniqueConstraint
)
from ._base import Base
from ..mixins import (
    GUIDPk,
    UserMixin,
    Timestamped,
    Created,
    LastUsed,
    ValidityWindow,
    ActiveToggle
)

# ------------------------------------------------------------------ helpers
def _new_digest() -> str:
    """
    Generate a brand‑new API‑key digest:

    1. 32‑byte URL‑safe random secret
    2. BLAKE2b‑256 hex digest
    """
    raw = secrets.token_urlsafe(32)
    return hashlib.blake2b(raw.encode(), digest_size=32).hexdigest()

# ------------------------------------------------------------------ model
class ApiKey(
    Base,
    GUIDPk,
    UserMixin,           # FK → user.id and back‑populates
    Created,             # created_at timestamp
    LastUsed,            # last_used_at timestamp
    ValidityWindow,      # expires_at
    ActiveToggle,        # is_active
):
    __tablename__  = "api_keys"
    __table_args__ = (UniqueConstraint("digest"),)

    label   = Column(String(120), nullable=False)

    digest  = Column(
        String(64),
        nullable=False,
        unique=True,
        default=_new_digest,                    # ← on‑create default
        info={
            "autoapi": {
                # hide from Create / Update / Replace verbs
                "disable_on": ["create", "update", "replace"],
                # show in READ / LIST responses only
                "read_only": True,
            }
        },
    )

    # ---------- helpers ------------------------------------
    def is_expired(self) -> bool:
        return self.valid_to is not None and datetime.now(timezone.utc) >= self.expires_at