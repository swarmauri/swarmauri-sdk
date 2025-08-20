from __future__ import annotations

from autoapi.v3.types import (
    Integer,
    LargeBinary,
    SAEnum,
    UniqueConstraint,
    relationship,
    PgUUID,
)
from sqlalchemy.orm import Mapped
from uuid import UUID
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk, Timestamped
from autoapi.v3.specs import acol, S, IO, F
from autoapi.v3.specs.io_spec import Pair
from autoapi.v3.specs.storage_spec import ForeignKeySpec
from autoapi.v3.decorators import hook_ctx

import base64
import secrets
from fastapi import HTTPException
from ..utils import b64d
from .key import Key, KeyAlg
from swarmauri_core.crypto.types import KeyType, KeyUse, ExportPolicy


class KeyVersion(Base, GUIDPk, Timestamped):
    __tablename__ = "key_versions"
    __resource__ = "key_version"
    __table_args__ = (UniqueConstraint("key_id", "version"),)

    key_id: Mapped[UUID] = acol(
        storage=S(
            type_=PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="keys.id", on_delete="CASCADE"),
            nullable=False,
            index=True,
        ),
        field=F(py_type=UUID, required_in=("create",)),
        io=IO(
            in_verbs=("create",),
            out_verbs=("read", "list"),
            filter_ops=("eq",),
        ),
    )

    version: Mapped[int] = acol(
        storage=S(type_=Integer, nullable=False),
        field=F(py_type=int, required_in=("create",)),
        io=IO(in_verbs=("create",), out_verbs=("read", "list"), sortable=True),
    )

    status: Mapped[str] = acol(
        storage=S(
            type_=SAEnum(
                "active",
                name="VersionStatus",
                native_enum=True,
                validate_strings=True,
                create_constraint=True,
            ),
            nullable=False,
        ),
        field=F(py_type=str, required_in=("create",)),
        io=IO(in_verbs=("create",), out_verbs=("read", "list")),
    )

    def _public_material_pair(ctx):
        temp = getattr(ctx, "temp", {})
        raw = temp.get("paired_values", {}).get("public_material", {}).get("raw")
        if raw is None:
            raw = base64.b64encode(secrets.token_bytes(32)).decode()
        return Pair(raw=raw, stored=b64d(raw))

    public_material: Mapped[bytes | memoryview | None] = acol(
        storage=S(type_=LargeBinary, nullable=True),
        io=IO(allow_in=False, allow_out=False).paired(
            _public_material_pair,
            alias="public_material_b64",
            verbs=("create", "update"),
        ),
    )

    key = relationship("Key", back_populates="versions", lazy="joined")

    @hook_ctx(ops="create", phase="PRE_HANDLER")
    async def _generate_material(cls, ctx):
        payload = ctx.setdefault("payload", {})
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
        raw = payload.get("public_material_b64")
        if raw is None:
            if key_obj.algorithm in (KeyAlg.AES256_GCM, KeyAlg.CHACHA20_POLY1305):
                material = secrets.token_bytes(32)
                payload["public_material_b64"] = base64.b64encode(material).decode()
            else:
                raise HTTPException(status_code=400, detail="Unsupported algorithm")
        else:
            material = b64d(raw)
        await secrets_drv.store_key(
            key_type=KeyType.SYMMETRIC,
            uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
            name=str(key_id),
            material=material,
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        )

    @hook_ctx(ops="create", phase="POST_HANDLER")
    async def _scrub_material(cls, ctx):
        """Remove raw key material from the response payload."""
        obj = ctx.get("result")
        if obj is not None:
            obj.public_material = None
