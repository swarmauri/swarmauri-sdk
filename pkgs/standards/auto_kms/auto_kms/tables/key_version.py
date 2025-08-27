from __future__ import annotations

import secrets
from uuid import UUID, uuid4

from fastapi import HTTPException

from autoapi.v3.decorators import hook_ctx
from autoapi.v3.specs import IO, F, S, acol
from autoapi.v3.specs.io_spec import Pair
from autoapi.v3.specs.storage_spec import ForeignKeySpec
from autoapi.v3.tables import Base
from autoapi.v3.types import (
    Integer,
    LargeBinary,
    PgUUID,
    SAEnum,
    UniqueConstraint,
    relationship,
    Mapped,
)
from swarmauri_core.crypto.types import ExportPolicy, KeyType, KeyUse

from ..utils import b64d
from .key import Key, KeyAlg


class KeyVersion(Base):
    __tablename__ = "key_versions"
    __resource__ = "key_version"
    __table_args__ = (UniqueConstraint("key_id", "version"),)

    # Provide explicit primary key to avoid mixin materialization issues in tests
    id: Mapped[UUID] = acol(
        storage=S(
            type_=PgUUID(as_uuid=True),
            primary_key=True,
            default=uuid4,
        ),
        field=F(py_type=UUID),
        io=IO(out_verbs=("read", "list")),
    )

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

    def _pair_material(ctx):
        payload = ctx.get("payload") or {}
        raw = payload.get("public_material_b64")
        if raw is None:
            return Pair(raw=None, stored=None)
        return Pair(raw=raw, stored=b64d(raw))

    public_material: Mapped[bytes | memoryview | None] = acol(
        storage=S(type_=LargeBinary, nullable=True),
        io=IO().paired(
            _pair_material, alias="public_material_b64", verbs=("create", "update")
        ),
    )

    key = relationship("Key", back_populates="versions", lazy="joined")

    @hook_ctx(ops="create", phase="POST_HANDLER")
    async def _generate_material(cls, ctx):
        obj = ctx.get("result")
        if obj is None or obj.public_material is not None:
            return
        secrets_drv = ctx.get("secrets")
        if secrets_drv is None:
            raise HTTPException(status_code=500, detail="Secrets driver missing")
        db = ctx.get("db")
        if db is None:
            raise HTTPException(status_code=500, detail="DB session missing")
        key_id = getattr(obj, "key_id", None)
        if key_id is None:
            raise HTTPException(status_code=400, detail="Missing key_id")
        key_obj = await db.get(Key, UUID(str(key_id)))
        if key_obj is None:
            raise HTTPException(status_code=404, detail="Key not found")
        if key_obj.algorithm in (KeyAlg.AES256_GCM, KeyAlg.CHACHA20_POLY1305):
            material = secrets.token_bytes(32)
        else:  # pragma: no cover - defensive
            raise HTTPException(status_code=400, detail="Unsupported algorithm")
        await secrets_drv.store_key(
            key_type=KeyType.SYMMETRIC,
            uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
            name=str(key_id),
            material=material,
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        )
        obj.public_material = material

    @hook_ctx(ops="create", phase="POST_RESPONSE")
    async def _scrub_material(cls, ctx):
        """Remove raw key material from the response payload."""
        obj = ctx.get("result")
        if obj is None:
            return
        if isinstance(obj, dict):
            obj.pop("public_material", None)
        else:
            obj.public_material = None
