from __future__ import annotations

from autoapi.v3.types import (
    Column,
    Integer,
    LargeBinary,
    SAEnum,
    ForeignKey,
    UniqueConstraint,
    relationship,
    PgUUID,
)
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk, Timestamped
from autoapi.v3.decorators import hook_ctx

from fastapi import HTTPException
from uuid import UUID
import secrets

from .key import Key, KeyAlg
from swarmauri_core.crypto.types import ExportPolicy, KeyType, KeyUse


class KeyVersion(Base, GUIDPk, Timestamped):
    __tablename__ = "key_versions"
    __resource__ = "key_version"
    __table_args__ = (UniqueConstraint("key_id", "version"),)

    key_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("keys.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version = Column(Integer, nullable=False)
    status = Column(
        SAEnum(
            "active",
            name="VersionStatus",
            native_enum=True,
            validate_strings=True,
            create_constraint=True,
        ),
        nullable=False,
    )
    public_material = Column(
        LargeBinary,
        nullable=True,
        info={
            "autoapi": {
                "disable_on": ["update", "replace"],
                "read_only": True,
            }
        },
    )

    key = relationship("Key", back_populates="versions", lazy="joined")

    @hook_ctx(ops="create", phase="PRE_HANDLER")
    async def _generate_material(cls, ctx):
        payload = ctx.setdefault("payload", {})
        if payload.get("public_material") is not None:
            return
        secrets_drv = ctx.get("secrets")
        if secrets_drv is None:
            raise HTTPException(status_code=500, detail="Secrets driver missing")
        db = ctx.get("db")
        if db is None:
            raise HTTPException(status_code=500, detail="DB session missing")
        key_id = payload.get("key_id")
        if key_id is None:
            raise HTTPException(status_code=400, detail="Missing key_id")
        key_obj = await db.get(Key, UUID(str(key_id)))
        if key_obj is None:
            raise HTTPException(status_code=404, detail="Key not found")
        if key_obj.algorithm in (KeyAlg.AES256_GCM, KeyAlg.CHACHA20_POLY1305):
            material = secrets.token_bytes(32)
        else:
            raise HTTPException(status_code=400, detail="Unsupported algorithm")
        await secrets_drv.store_key(
            key_type=KeyType.SYMMETRIC,
            uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
            name=str(key_id),
            material=material,
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        )
        # Persist the generated key material on the version so that downstream
        # crypto providers that require direct material access can operate.
        # This mirrors the behavior during initial key creation where the
        # material is stored with the primary version. Without this assignment
        # the database row ends up with ``public_material`` as ``NULL``,
        # triggering "Key material missing" errors during encrypt/decrypt
        # operations when the provider expects the material to be present on the
        # key version record.
        payload["public_material"] = material

    @hook_ctx(ops="create", phase="POST_HANDLER")
    async def _scrub_material(cls, ctx):
        """Remove raw key material from the response payload."""
        obj = ctx.get("result")
        if obj is not None:
            obj.public_material = None
