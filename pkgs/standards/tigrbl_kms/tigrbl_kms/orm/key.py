# tigrbl_kms/orm/key.py
from __future__ import annotations
import base64
from enum import Enum
from uuid import UUID, uuid4
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import String, Integer, Enum as SAEnum
from tigrbl.types import Mapped, relationship
from tigrbl.orm.mixins import BulkCapable, Replaceable

from tigrbl.orm.tables import Base
from tigrbl.specs import acol, vcol, S, F, IO
from tigrbl.hook import hook_ctx
from tigrbl.op import op_ctx
from fastapi import HTTPException, Response

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


def _alg_to_provider(alg: KeyAlg | str) -> Optional[str]:
    """Translate a :class:`KeyAlg` into the algorithm string expected by crypto providers."""
    alg_val = alg.value if isinstance(alg, KeyAlg) else alg
    if alg_val == KeyAlg.AES256_GCM.value:
        return "AES-256-GCM"
    if alg_val in (KeyAlg.RSA2048.value, KeyAlg.RSA3072.value):
        return None
    return alg_val


class KeyStatus(str, Enum):
    enabled = "enabled"
    disabled = "disabled"


class Key(Base, BulkCapable, Replaceable):
    __tablename__ = "keys"
    __resource__ = "key"
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
        storage=S(type_=String(120), unique=True, index=True, nullable=False),
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
    kid: Optional[str] = vcol(
        io=IO(out_verbs=("encrypt", "wrap")),
        read_producer=lambda obj, ctx: str(getattr(obj, "id", "")),
    )

    plaintext_b64: Optional[str] = vcol(
        field=F(required_in=("encrypt",)),
        io=IO(in_verbs=("encrypt",), out_verbs=("decrypt",)),
    )

    aad_b64: Optional[str] = vcol(
        field=F(allow_null_in=("encrypt", "decrypt")),
        io=IO(
            in_verbs=("encrypt", "decrypt", "wrap", "unwrap"),
            out_verbs=("encrypt", "wrap", "unwrap"),
        ),
    )

    nonce_b64: Optional[str] = vcol(
        field=F(required_in=("decrypt", "unwrap"), allow_null_in=("encrypt", "wrap")),
        io=IO(in_verbs=("encrypt", "decrypt", "unwrap"), out_verbs=("encrypt", "wrap")),
    )

    alg: Optional[KeyAlg] = vcol(
        field=F(py_type=KeyAlg, allow_null_in=("encrypt", "decrypt", "wrap", "unwrap")),
        io=IO(
            in_verbs=("encrypt", "decrypt", "wrap", "unwrap"),
            out_verbs=("encrypt", "wrap"),
        ),
    )

    ciphertext_b64: Optional[str] = vcol(
        field=F(required_in=("decrypt",)),
        io=IO(in_verbs=("decrypt",), out_verbs=("encrypt",)),
    )

    tag_b64: Optional[str] = vcol(
        field=F(allow_null_in=("encrypt", "decrypt", "wrap", "unwrap")),
        io=IO(in_verbs=("decrypt", "unwrap"), out_verbs=("encrypt", "wrap")),
    )

    version: Optional[int] = vcol(
        field=F(py_type=int),
        io=IO(out_verbs=("encrypt", "wrap")),
    )

    # ---- Key Wrapping virtual columns ----
    key_material_b64: Mapped[Optional[str]] = vcol(
        field=F(required_in=("wrap",)),
        io=IO(in_verbs=("wrap",), out_verbs=("unwrap",)),
    )

    wrapped_key_b64: Mapped[Optional[str]] = vcol(
        field=F(required_in=("unwrap",)),
        io=IO(in_verbs=("unwrap",), out_verbs=("wrap",)),
    )

    # ---- Hook: seed key material on create ----
    @hook_ctx(ops=("create", "bulk_create"), phase="POST_HANDLER")
    async def _seed_primary_version(cls, ctx):
        import secrets
        from .key_version import KeyVersion

        db = ctx.get("db")
        result = ctx.get("result")
        if db is None or result is None:
            raise HTTPException(status_code=500, detail="DB session missing")

        keys = result if isinstance(result, list) else [result]

        for key_obj in keys:
            if key_obj.algorithm != KeyAlg.AES256_GCM:
                continue  # only symmetric keys supported for now

            existing = await KeyVersion.handlers.list.core(
                {
                    "db": db,
                    "payload": {
                        "filters": {
                            "key_id": key_obj.id,
                            "version": key_obj.primary_version,
                        }
                    },
                }
            )
            if not existing:
                material = secrets.token_bytes(32)
                kv = KeyVersion(
                    key_id=key_obj.id,
                    version=key_obj.primary_version,
                    status="active",
                    public_material=material,
                )
                db.add(kv)

    @hook_ctx(
        ops=("create", "read", "list", "update", "replace", "wrap", "unwrap"),
        phase="POST_RESPONSE",
    )
    async def _scrub_version_material(cls, ctx):
        obj = ctx.get("result")
        if obj is None:
            return

        def scrub(o):
            from fastapi import Response as _FastAPIResponse

            if isinstance(o, _FastAPIResponse):
                return o
            if isinstance(o, dict):
                data = dict(o)
            elif hasattr(o, "model_dump") and callable(getattr(o, "model_dump")):
                data = o.model_dump()
            elif hasattr(o, "dict") and callable(getattr(o, "dict")):
                data = o.dict()  # type: ignore[call-arg]
            elif hasattr(o, "__dict__") and not isinstance(o, type):
                data = {k: v for k, v in vars(o).items() if not k.startswith("_")}
            else:
                try:
                    data = dict(o)
                except Exception:
                    return o

            if isinstance(data, dict):
                data.pop("versions", None)
                from fastapi.encoders import jsonable_encoder

                cleaned: dict = {}
                for k, v in data.items():
                    try:
                        cleaned[k] = jsonable_encoder(v, sqlalchemy_safe=True)
                    except Exception:
                        cleaned[k] = str(v)
                return cleaned
            return data

        if isinstance(obj, list):
            ctx["result"] = [scrub(i) for i in obj]
        else:
            ctx["result"] = scrub(obj)

    # ---- Hook: ensure key exists & enabled ----
    @hook_ctx(
        ops=("encrypt", "decrypt", "wrap", "unwrap", "rotate"), phase="PRE_HANDLER"
    )
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
    )
    async def encrypt(cls, ctx):
        from ..utils import b64d, b64d_optional

        p = ctx.get("payload") or {}
        crypto = getattr(
            getattr(ctx.get("request"), "state", object()), "crypto", None
        ) or ctx.get("crypto")
        if crypto is None:
            raise HTTPException(status_code=500, detail="Crypto provider missing")

        import binascii

        try:
            aad = b64d_optional(p.get("aad_b64"))
        except binascii.Error as exc:  # pragma: no cover - defensive
            raise HTTPException(
                status_code=400, detail="Invalid base64 encoding for aad_b64"
            ) from exc
        try:
            nonce = b64d_optional(p.get("nonce_b64"))
        except binascii.Error as exc:  # pragma: no cover - defensive
            raise HTTPException(
                status_code=400, detail="Invalid base64 encoding for nonce_b64"
            ) from exc
        try:
            pt = b64d(p["plaintext_b64"])
        except binascii.Error as exc:  # pragma: no cover - defensive
            raise HTTPException(
                status_code=400, detail="Invalid base64 encoding for plaintext_b64"
            ) from exc
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
                material=bytes(version.public_material),
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
    )
    async def decrypt(cls, ctx):
        from ..utils import b64d, b64d_optional

        p = ctx.get("payload") or {}
        crypto = getattr(
            getattr(ctx.get("request"), "state", object()), "crypto", None
        ) or ctx.get("crypto")
        if crypto is None:
            raise HTTPException(status_code=500, detail="Crypto provider missing")

        import binascii

        try:
            aad = b64d_optional(p.get("aad_b64"))
        except binascii.Error as exc:  # pragma: no cover - defensive
            raise HTTPException(
                status_code=400, detail="Invalid base64 encoding for aad_b64"
            ) from exc
        try:
            nonce = b64d(p["nonce_b64"])
        except binascii.Error as exc:  # pragma: no cover - defensive
            raise HTTPException(
                status_code=400, detail="Invalid base64 encoding for nonce_b64"
            ) from exc
        try:
            ct = b64d(p["ciphertext_b64"])
        except binascii.Error as exc:  # pragma: no cover - defensive
            raise HTTPException(
                status_code=400, detail="Invalid base64 encoding for ciphertext_b64"
            ) from exc
        try:
            tag = b64d_optional(p.get("tag_b64"))
        except binascii.Error as exc:  # pragma: no cover - defensive
            raise HTTPException(
                status_code=400, detail="Invalid base64 encoding for tag_b64"
            ) from exc
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
                material=bytes(version.public_material),
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

    @op_ctx(
        alias="wrap",
        target="custom",
        arity="member",  # /key/{item_id}/wrap
        persist="skip",
    )
    async def wrap(cls, ctx):
        """Wrap (encrypt) key material using this key."""
        from ..utils import b64d, b64d_optional

        p = ctx.get("payload") or {}
        crypto = getattr(
            getattr(ctx.get("request"), "state", object()), "crypto", None
        ) or ctx.get("crypto")
        if crypto is None:
            raise HTTPException(status_code=500, detail="Crypto provider missing")

        import binascii

        # Validate and decode the key material to be wrapped
        try:
            key_material = b64d(p["key_material_b64"])
        except binascii.Error as exc:
            raise HTTPException(
                status_code=400, detail="Invalid base64 encoding for key_material_b64"
            ) from exc
        except KeyError:
            raise HTTPException(status_code=400, detail="key_material_b64 is required")

        # Optional AAD for key wrapping context
        try:
            aad = b64d_optional(p.get("aad_b64"))
        except binascii.Error as exc:
            raise HTTPException(
                status_code=400, detail="Invalid base64 encoding for aad_b64"
            ) from exc

        kid = str(ctx["key"].id)
        key_obj = ctx["key"]
        if key_obj.status != KeyStatus.enabled:
            raise HTTPException(status_code=403, detail="Key is disabled")
        if key_obj.algorithm not in (KeyAlg.AES256_GCM, KeyAlg.CHACHA20_POLY1305):
            raise HTTPException(
                status_code=400,
                detail="Key wrapping only supported for AES256_GCM and CHACHA20_POLY1305",
            )
        alg_str = _alg_to_provider(key_obj.algorithm)

        from swarmauri_core.crypto.types import (
            ExportPolicy,
            KeyRef,
            KeyType,
            KeyUse,
        )

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
            uses=(KeyUse.WRAP, KeyUse.UNWRAP),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            material=bytes(version.public_material),
        )

        try:
            ct = await crypto.encrypt(
                key_ref,
                key_material,
                alg=alg_str,
                nonce=None,
                aad=aad,
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail="Key wrapping failed") from exc

        return {
            "kid": kid,
            "version": ct.version,
            "alg": key_obj.algorithm,
            "nonce_b64": base64.b64encode(ct.nonce).decode(),
            "wrapped_key_b64": base64.b64encode(ct.ct).decode(),
            "tag_b64": base64.b64encode(ct.tag).decode(),
            "aad_b64": p.get("aad_b64"),
        }

    @op_ctx(
        alias="unwrap",
        target="custom",
        arity="member",  # /key/{item_id}/unwrap
        persist="skip",
    )
    async def unwrap(cls, ctx):
        """Unwrap (decrypt) wrapped key material using this key."""
        from ..utils import b64d, b64d_optional

        p = ctx.get("payload") or {}
        crypto = getattr(
            getattr(ctx.get("request"), "state", object()), "crypto", None
        ) or ctx.get("crypto")
        if crypto is None:
            raise HTTPException(status_code=500, detail="Crypto provider missing")

        import binascii

        # Validate and decode required fields
        try:
            wrapped_key = b64d(p["wrapped_key_b64"])
        except binascii.Error as exc:
            raise HTTPException(
                status_code=400, detail="Invalid base64 encoding for wrapped_key_b64"
            ) from exc
        except KeyError:
            raise HTTPException(status_code=422, detail="wrapped_key_b64 is required")

        try:
            nonce = b64d(p["nonce_b64"])
        except binascii.Error as exc:
            raise HTTPException(
                status_code=400, detail="Invalid base64 encoding for nonce_b64"
            ) from exc
        except KeyError:
            raise HTTPException(status_code=422, detail="nonce_b64 is required")

        try:
            tag = b64d_optional(p.get("tag_b64"))
        except binascii.Error as exc:
            raise HTTPException(
                status_code=400, detail="Invalid base64 encoding for tag_b64"
            ) from exc

        try:
            aad = b64d_optional(p.get("aad_b64"))
        except binascii.Error as exc:
            raise HTTPException(
                status_code=400, detail="Invalid base64 encoding for aad_b64"
            ) from exc

        kid = str(ctx["key"].id)
        key_obj = ctx["key"]
        if key_obj.status != KeyStatus.enabled:
            raise HTTPException(status_code=403, detail="Key is disabled")
        alg_str = _alg_to_provider(key_obj.algorithm)

        from swarmauri_core.crypto.types import (
            AEADCiphertext,
            ExportPolicy,
            KeyRef,
            KeyType,
            KeyUse,
        )

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
            uses=(KeyUse.UNWRAP, KeyUse.WRAP),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            material=bytes(version.public_material),
        )

        if tag is None:
            raise HTTPException(status_code=422, detail="tag_b64 is required")

        ct = AEADCiphertext(
            kid=kid,
            version=key_obj.primary_version,
            alg=alg_str or "",
            nonce=nonce,
            ct=wrapped_key,
            tag=tag,
            aad=aad,
        )

        try:
            key_material = await crypto.decrypt(key_ref, ct, aad=aad)
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail="Key unwrapping failed"
            ) from exc

        return {"key_material_b64": base64.b64encode(key_material).decode()}

    @op_ctx(
        alias="rotate",
        target="custom",
        arity="member",  # /key/{item_id}/rotate
        status_code=201,
    )
    async def rotate(cls, ctx):
        import secrets
        from .key_version import KeyVersion

        db = ctx.get("db")
        key_obj = ctx.get("key")
        if db is None or key_obj is None:
            raise HTTPException(status_code=500, detail="Required context missing")
        if key_obj.algorithm != KeyAlg.AES256_GCM:
            raise HTTPException(status_code=400, detail="Unsupported algorithm")

        new_version = key_obj.primary_version + 1
        material = secrets.token_bytes(32)
        kv = KeyVersion(
            key_id=key_obj.id,
            version=new_version,
            status="active",
            public_material=material,
        )
        key_obj.primary_version = new_version
        db.add(kv)

    @hook_ctx(ops="rotate", phase="POST_RESPONSE")
    async def _rotate_empty_body(cls, ctx):
        ctx["result"] = Response(status_code=201)
