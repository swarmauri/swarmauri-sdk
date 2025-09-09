from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import HTTPException, Response

from tigrbl.v3.hook import hook_ctx
from tigrbl.v3.specs import IO, F, S, acol
from tigrbl.v3.orm.mixins import BulkCapable, Replaceable
from tigrbl.v3.column.io_spec import Pair
from tigrbl.v3.column.storage_spec import ForeignKeySpec
from tigrbl.v3.orm.tables import Base
from tigrbl.v3.types import (
    Integer,
    LargeBinary,
    PgUUID,
    SAEnum,
    UniqueConstraint,
    relationship,
    Mapped,
)
from swarmauri_core.crypto.types import ExportPolicy, KeyUse
from swarmauri_core.keys.types import KeySpec, KeyClass, KeyAlg as ProviderKeyAlg

from ..utils import b64d
from .key import Key, KeyAlg


class KeyVersion(Base, BulkCapable, Replaceable):
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

    # ---- Hooks: allow single-object bulk_create ----
    @hook_ctx(ops="bulk_create", phase="PRE_HANDLER")
    async def _coerce_single_bulk_create(cls, ctx):
        payload = ctx.get("payload")
        if isinstance(payload, dict):
            ctx["payload"] = [payload]
            ctx["_single_bulk"] = True

    @hook_ctx(ops="bulk_create", phase="POST_RESPONSE")
    async def _unwrap_single_bulk_create(cls, ctx):
        if ctx.pop("_single_bulk", False):
            result = ctx.get("result")
            if isinstance(result, list):
                ctx["result"] = result[0] if result else None
            resp = ctx.get("response")
            if isinstance(resp, Response):
                resp.status_code = 201

    @hook_ctx(ops=("create", "bulk_create"), phase="POST_HANDLER")
    async def _generate_material(cls, ctx):
        objs = ctx.get("result")
        if objs is None:
            return
        items = objs if isinstance(objs, list) else [objs]
        key_provider = ctx.get("key_provider")
        if key_provider is None:
            raise HTTPException(status_code=500, detail="Key provider missing")
        db = ctx.get("db")
        if db is None:
            raise HTTPException(status_code=500, detail="DB session missing")
        for obj in items:
            if getattr(obj, "public_material", None) is not None:
                continue
            key_id = getattr(obj, "key_id", None)
            if key_id is None:
                raise HTTPException(status_code=400, detail="Missing key_id")
            key_obj = await db.get(Key, UUID(str(key_id)))
            if key_obj is None:
                raise HTTPException(status_code=404, detail="Key not found")
            if key_obj.algorithm in (KeyAlg.AES256_GCM, KeyAlg.CHACHA20_POLY1305):
                material = await key_provider.random_bytes(32)
            else:  # pragma: no cover - defensive
                raise HTTPException(status_code=400, detail="Unsupported algorithm")
            await key_provider.import_key(
                KeySpec(
                    klass=KeyClass.symmetric,
                    alg=ProviderKeyAlg.AES256_GCM,
                    uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
                    export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
                    label=str(key_id),
                ),
                material,
            )
            obj.public_material = material

    @hook_ctx(ops=("create", "bulk_create"), phase="POST_RESPONSE")
    async def _scrub_material(cls, ctx):
        """Remove raw key material from the response payload."""
        obj = ctx.get("result")
        if obj is None:
            return
        if isinstance(obj, list):
            for o in obj:
                if isinstance(o, dict):
                    o.pop("public_material", None)
                else:
                    o.public_material = None
        elif isinstance(obj, dict):
            obj.pop("public_material", None)
        else:
            obj.public_material = None
