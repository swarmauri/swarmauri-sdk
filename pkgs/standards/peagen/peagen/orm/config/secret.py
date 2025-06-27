"""
peagen.orm.config.secret
===========================

Tenant-scoped secret storage.

Design Highlights
-----------------
• Every secret belongs to **one Tenant**.
• `name` is unique within that tenant (case-sensitive).
• `cipher` holds the encrypted payload (Base64 or AEAD ciphertext).
• Optional `owner_user_id` lets you track who created / owns the secret.
• The raw key is **never** stored – it lives in an external KMS / Vault.
"""

from __future__ import annotations

import uuid
from sqlalchemy import String, Text, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..tenant.user import UserModel
from ..tenant.tenant import TenantModel

from ..base import BaseModel


class SecretModel(BaseModel):
    """
    Workspace-level secret (token, password, certificate …).
    """

    __tablename__ = "secrets"

    # ───────────────────── Columns ─────────────────────
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Optional reference to the user who created / owns this secret
    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="Logical secret name, unique per tenant.",
    )

    cipher: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Encrypted (base64-encoded) value; decrypted via KMS/Vault.",
    )

    description: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        doc="Optional free-text description.",
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_secret_per_tenant"),
    )

    # ───────────────── Relationships ───────────────────
    tenant: Mapped["TenantModel"] = relationship("TenantModel", lazy="selectin")

    owner: Mapped[UserModel | None] = relationship("UserModel", lazy="selectin")

    # ───────────────────── Magic ───────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Secret id={self.id} tenant={self.tenant_id} "
            f"name={self.name!r} owner={self.owner_user_id or '∅'}>"
        )


Secret = SecretModel
