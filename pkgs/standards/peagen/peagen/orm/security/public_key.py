"""
peagen.orm.security.public_key
=================================

User-owned public key (SSH, Ed25519, or GPG) used for authentication or
signature verification.

Design Highlights
-----------------
• **Global User scope** – every key is bound to exactly one User.
• **Never encrypted** – public keys are, by definition, non-secret;
  if you need private keys, store them in `DeployKey` or a secrets vault.
• Uniqueness constraints:
    • (`user_id`, `name`) – a user cannot reuse a label.
    • `fingerprint` – one fingerprint in the entire system.
• Supports soft-revocation via `revoked` + `revoked_at`.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    String,
    Text,
    Boolean,
    TIMESTAMP,
    UniqueConstraint,
    ForeignKey,
    Enum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - imports for type hints
    from ..tenant.user import UserModel

from ..base import BaseModel


class KeyType(str, enum.Enum):
    """Supported public-key algorithms."""

    ssh_rsa = "ssh-rsa"
    ssh_ed25519 = "ssh-ed25519"
    ssh_ecdsa = "ssh-ecdsa"
    pgp = "pgp"  # ASCII-armored PGP public key


class PublicKeyModel(BaseModel):
    """
    Public key linked to a user identity.
    """

    __tablename__ = "public_keys"

    # ───────────────────── Columns ─────────────────────
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="Human-friendly label, e.g., 'laptop-ssh', unique per user.",
    )

    key_type: Mapped[KeyType] = mapped_column(
        Enum(KeyType, name="public_key_type_enum"),
        nullable=False,
        default=KeyType.ssh_ed25519,
    )

    key_data: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Raw public-key string (RFC-4253 or ASCII-armored PGP).",
    )

    fingerprint: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
        doc="Unique SHA256/MD5 fingerprint for quick look-ups.",
    )

    revoked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="Soft deletion flag. Keep key for audit, block auth.",
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        doc="When the key was revoked (UTC).",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_public_key_label_per_user"),
    )

    # ───────────────── Relationships ───────────────────
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="public_keys",
        lazy="selectin",
    )

    # ───────────────────── Magic ───────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        status = "revoked" if self.revoked else "active"
        return (
            f"<PublicKey id={self.id} user={self.user_id} "
            f"type={self.key_type} status={status}>"
        )
