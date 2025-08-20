# auto_kms/tables/key.py
from __future__ import annotations
from enum import Enum
from uuid import UUID, uuid4
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import String, Integer, Enum as SAEnum
from sqlalchemy.orm import Mapped, relationship

from autoapi.v3.tables import Base
from autoapi.v3.specs import acol, vcol, S, F, IO
from autoapi.v3.decorators import schema_ctx, hook_ctx, op_ctx
from autoapi.v3.opspec.types import SchemaRef
from fastapi import HTTPException
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .key_version import KeyVersion

# Prefer PG UUID type class; fall back to String class
try:
    from sqlalchemy.dialects.postgresql import UUID as PGUUID

    _UUID_TYPE = PGUUID  # type CLASS (binder instantiates)
except Exception:
    _UUID_TYPE = String  # type CLASS


class KeyAlg(str, Enum):
    AES256_GCM = "AES256_GCM"
    CHACHA20_POLY1305 = "CHACHA20_POLY1305"
    RSA2048 = "RSA2048"
    RSA3072 = "RSA3072"


def _alg_to_provider(alg: KeyAlg | str) -> str:
    """Translate a :class:`KeyAlg` into the algorithm string expected by crypto providers."""
    alg_val = alg.value if isinstance(alg, KeyAlg) else alg
    return "AES-256-GCM" if alg_val == KeyAlg.AES256_GCM.value else alg_val


class KeyStatus(str, Enum):
    enabled = "enabled"
    disabled = "disabled"


class Key(Base):
    __tablename__ = "keys"
    __allow_unmapped__ = True  # allow vcol attributes

    # Persisted columns (py_type inferred from annotation; SA dtype via StorageSpec.type_)
    id: Mapped[UUID] = acol(
        storage=S(
            type_=_UUID_TYPE,
            primary_key=True,
            index=True,
            nullable=False,
            default=uuid4,
        ),
        io=IO(out_verbs=("read", "list"), sortable=True),
    )

    name: Mapped[str] = acol(
        storage=S(type_=String, unique=True, index=True, nullable=False),
        field=F(constraints={"max_length": 120}, required_in=("create",)),
        io=IO(
            in_verbs=("create", "update", "replace"),
            out_verbs=("read", "list"),
            sortable=True,
            filter_ops=("eq", "ilike"),
        ),
    )

    # in Key model, for enums:
    algorithm = acol(
        storage=S(type_=SAEnum, nullable=False),
        field=F(py_type=KeyAlg, required_in=("create",)),  # <— explicit
        io=IO(in_verbs=("create",), out_verbs=("read", "list")),
    )
    status = acol(
        storage=S(type_=SAEnum, nullable=False, default=KeyStatus.enabled),
        field=F(py_type=KeyStatus),  # <— explicit
        io=IO(
            in_verbs=("update",),
            out_verbs=("read", "list"),
            filter_ops=("eq",),
            sortable=True,
        ),
    )

    primary_version: Mapped[int] = acol(
        storage=S(type_=Integer, nullable=False, default=1),
        io=IO(out_verbs=("read", "list")),  # read-only exposure
    )

    # Relationship
    versions: Mapped[List["KeyVersion"]] = relationship(
        back_populates="key", lazy="selectin", cascade="all, delete-orphan"
    )

    # Virtual (wire-only)
    kid: str = vcol(
        io=IO(out_verbs=("read", "list")),
        read_producer=lambda obj, ctx: str(getattr(obj, "id", "")),
    )

    # ---- Schemas (for ops) ----
    @schema_ctx(alias="Encrypt", kind="in")
    class EncryptIn(BaseModel):
        plaintext_b64: str = Field(..., description="Base64 plaintext")
        aad_b64: Optional[str] = None
        nonce_b64: Optional[str] = None
        alg: Optional[KeyAlg] = None

    @schema_ctx(alias="Encrypt", kind="out")
    class EncryptOut(BaseModel):
        kid: str
        version: int
        alg: KeyAlg
        nonce_b64: str
        ciphertext_b64: str
        tag_b64: Optional[str] = None
        aad_b64: Optional[str] = None

    @schema_ctx(alias="Decrypt", kind="in")
    class DecryptIn(BaseModel):
        ciphertext_b64: str
        nonce_b64: str
        tag_b64: Optional[str] = None
        aad_b64: Optional[str] = None
        alg: Optional[KeyAlg] = None

    @schema_ctx(alias="Decrypt", kind="out")
    class DecryptOut(BaseModel):
        plaintext_b64: str

    # ---- Hook: ensure key exists & enabled ----
    @hook_ctx(ops=("encrypt", "decrypt"), phase="PRE_HANDLER")
    async def _ensure_key_enabled(cls, ctx):
        pp = ctx.get("path_params") or {}
        ident = pp.get("id") or pp.get("item_id")
        if not ident:
            raise HTTPException(status_code=400, detail="Missing key identifier")
        try:
            ident = ident if isinstance(ident, UUID) else UUID(str(ident))
        except Exception:
            raise HTTPException(status_code=422, detail="Invalid UUID for key id")

        db = ctx.get("db")
        if db is None:
            raise HTTPException(status_code=500, detail="DB session missing")
        # works with sync or async session
        getter = getattr(db, "get", None)
        obj = (
            await getter(cls, ident)
            if callable(getter)
            and getattr(getter, "__code__", None)
            and getter.__code__.co_flags & 0x80
            else db.get(cls, ident)
        )
        if obj is None:
            raise HTTPException(status_code=404, detail="Key not found")
        if obj.status == KeyStatus.disabled:
            raise HTTPException(status_code=403, detail="Key is disabled")
        ctx["key"] = obj

    # ---- Ops: ctx-only crypto (no DB writes) ----
    @op_ctx(
        alias="encrypt",
        target="custom",
        arity="member",  # /key/{item_id}/encrypt
        persist="skip",
        request_schema=SchemaRef("Encrypt", "in"),
        response_schema=SchemaRef("Encrypt", "out"),
    )
    async def encrypt(cls, ctx):
        import base64

        p = ctx.get("payload") or {}
        crypto = getattr(
            getattr(ctx.get("request"), "state", object()), "crypto", None
        ) or ctx.get("crypto")
        if crypto is None:
            raise HTTPException(status_code=500, detail="Crypto provider missing")

        aad = base64.b64decode(p["aad_b64"]) if p.get("aad_b64") else None
        nonce = base64.b64decode(p["nonce_b64"]) if p.get("nonce_b64") else None
        pt = base64.b64decode(p["plaintext_b64"])
        kid = str(ctx["key"].id)
        alg_in = p.get("alg") or ctx["key"].algorithm
        alg_enum = alg_in if isinstance(alg_in, KeyAlg) else KeyAlg(alg_in)
        alg_str = _alg_to_provider(alg_enum)

        import inspect
        from swarmauri_core.crypto.types import (
            ExportPolicy,
            KeyRef,
            KeyType,
            KeyUse,
        )

        try:
            inspect.signature(crypto.encrypt).parameters["kid"]
        except KeyError:
            key_obj = ctx["key"]
            version = next(
                (v for v in key_obj.versions if v.version == key_obj.primary_version),
                None,
            )
            if version is None or version.public_material is None:
                raise HTTPException(status_code=500, detail="Key material missing")
            key_ref = KeyRef(
                kid=kid,
                version=key_obj.primary_version,
                type=KeyType.SYMMETRIC,
                uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
                export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
                material=version.public_material,
            )
            res = await crypto.encrypt(
                key_ref,
                pt,
                alg=alg_str,
                aad=aad,
                nonce=nonce,
            )
        else:
            res = await crypto.encrypt(
                kid=kid, plaintext=pt, alg=alg_str, aad=aad, nonce=nonce
            )

        return {
            "kid": kid,
            "version": getattr(res, "version", ctx["key"].primary_version),
            "alg": alg_enum,
            "nonce_b64": base64.b64encode(getattr(res, "nonce")).decode(),
            "ciphertext_b64": base64.b64encode(getattr(res, "ct")).decode(),
            "tag_b64": (
                base64.b64encode(getattr(res, "tag")).decode()
                if getattr(res, "tag", None)
                else None
            ),
            "aad_b64": p.get("aad_b64"),
        }

    @op_ctx(
        alias="decrypt",
        target="custom",
        arity="member",  # /key/{item_id}/decrypt
        persist="skip",
        request_schema=SchemaRef("Decrypt", "in"),
        response_schema=SchemaRef("Decrypt", "out"),
    )
    async def decrypt(cls, ctx):
        import base64

        p = ctx.get("payload") or {}
        crypto = getattr(
            getattr(ctx.get("request"), "state", object()), "crypto", None
        ) or ctx.get("crypto")
        if crypto is None:
            raise HTTPException(status_code=500, detail="Crypto provider missing")

        aad = base64.b64decode(p["aad_b64"]) if p.get("aad_b64") else None
        nonce = base64.b64decode(p["nonce_b64"])
        ct = base64.b64decode(p["ciphertext_b64"])
        tag = base64.b64decode(p["tag_b64"]) if p.get("tag_b64") else None
        kid = str(ctx["key"].id)
        alg_in = p.get("alg") or ctx["key"].algorithm
        alg_enum = alg_in if isinstance(alg_in, KeyAlg) else KeyAlg(alg_in)
        alg_str = _alg_to_provider(alg_enum)

        import inspect
        from swarmauri_core.crypto.types import (
            AEADCiphertext,
            ExportPolicy,
            KeyRef,
            KeyType,
            KeyUse,
        )

        try:
            inspect.signature(crypto.decrypt).parameters["kid"]
        except KeyError:
            key_obj = ctx["key"]
            version = next(
                (v for v in key_obj.versions if v.version == key_obj.primary_version),
                None,
            )
            if version is None or version.public_material is None:
                raise HTTPException(status_code=500, detail="Key material missing")
            key_ref = KeyRef(
                kid=kid,
                version=key_obj.primary_version,
                type=KeyType.SYMMETRIC,
                uses=(KeyUse.DECRYPT, KeyUse.ENCRYPT),
                export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
                material=version.public_material,
            )
            ct_obj = AEADCiphertext(
                kid=kid,
                version=key_obj.primary_version,
                alg=alg_str,
                nonce=nonce,
                ct=ct,
                tag=tag or b"",
                aad=aad,
            )
            pt = await crypto.decrypt(key_ref, ct_obj, aad=aad)
        else:
            pt = await crypto.decrypt(
                kid=kid, ciphertext=ct, nonce=nonce, tag=tag, aad=aad, alg=alg_str
            )

        return {"plaintext_b64": base64.b64encode(pt).decode()}
