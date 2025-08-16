from __future__ import annotations

from typing import Any, Mapping

from autoapi.v3.types import Column, String, SAEnum, Integer, relationship, HookProvider
from autoapi.v3.decorators import op_ctx
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk, Timestamped
from swarmauri_core.crypto.types import AEADCiphertext, WrappedKey


class Key(Base, GUIDPk, Timestamped, HookProvider):
    __tablename__ = "keys"

    name = Column(String(120), nullable=False, index=True)
    algorithm = Column(SAEnum("AES256_GCM", name="KeyAlg"), nullable=False)
    status = Column(SAEnum("enabled", name="KeyStatus"), nullable=False)
    primary_version = Column(Integer, default=1, nullable=False)

    versions = relationship("KeyVersion", back_populates="key", lazy="selectin")

    @classmethod
    def _params(cls, ctx) -> Mapping[str, Any]:
        """Extract parameters from context."""
        from ..utils import params

        return params(ctx)

    # -------------------- Custom KMS operations (v3 OpSpecs) --------------------
    # Each op validates payload (optional), runs in unified lifecycle, and returns raw dicts.

    @op_ctx(alias="create", arity="collection", persist="default", returns="raw")
    async def create_op(self, *, ctx, db, request, payload):
        from ..utils import (
            coerce_key_type_from_params,
            coerce_uses_from_params,
            coerce_export_policy,
            asdict_desc,
        )

        p = self._params(ctx)
        sd = ctx["_kms_secrets"]
        desc = await sd.store_key(
            key_type=coerce_key_type_from_params(p),
            uses=coerce_uses_from_params(p),
            name=p.get("name"),
            material=None,
            export_policy=coerce_export_policy(p.get("export_policy")),
            tags=p.get("tags"),
        )
        return asdict_desc(desc)

    @op_ctx(alias="rotate", arity="member", persist="default", returns="raw")
    async def rotate(self, *, ctx, db, request, payload):
        from ..utils import auth_tenant_from_ctx, asdict_desc

        p = self._params(ctx)
        sd = ctx["_kms_secrets"]
        desc = await sd.rotate(
            kid=p["kid"],
            material=None,
            make_primary=bool(p.get("make_primary", True)),
            tags=p.get("tags"),
            tenant=auth_tenant_from_ctx(ctx),
        )
        return asdict_desc(desc)

    @op_ctx(alias="disable", arity="member", persist="default", returns="raw")
    async def disable(self, *, ctx, db, request, payload):
        from ..utils import auth_tenant_from_ctx, asdict_desc

        p = self._params(ctx)
        sd = ctx["_kms_secrets"]
        desc = await sd.set_state(
            kid=p["kid"], state="disabled", tenant=auth_tenant_from_ctx(ctx)
        )
        return asdict_desc(desc)

    @op_ctx(alias="encrypt", arity="member", persist="skip", returns="raw")
    async def encrypt(self, *, ctx, db, request, payload):
        from ..utils import b64e, b64d, b64d_optional, auth_tenant_from_ctx

        p = self._params(ctx)
        sd = ctx["_kms_secrets"]
        cp = ctx["_kms_crypto"]
        key = await sd.load_key(
            kid=p["kid"],
            version=p.get("version"),
            require_private=False,
            tenant=auth_tenant_from_ctx(ctx),
        )
        ct = await cp.encrypt(
            key,
            b64d(p["plaintext_b64"]),
            alg=p.get("alg"),
            aad=b64d_optional(p.get("aad_b64")),
            nonce=b64d_optional(p.get("nonce_b64")),
        )
        return {
            "kid": ct.kid,
            "version": ct.version,
            "alg": ct.alg,
            "nonce_b64": b64e(ct.nonce),
            "ciphertext_b64": b64e(ct.ct),
            "tag_b64": b64e(ct.tag),
            **({"aad_b64": b64e(ct.aad)} if ct.aad else {}),
        }

    @op_ctx(alias="decrypt", arity="member", persist="skip", returns="raw")
    async def decrypt(self, *, ctx, db, request, payload):
        from ..utils import b64e, b64d, b64d_optional, auth_tenant_from_ctx

        p = self._params(ctx)
        sd = ctx["_kms_secrets"]
        cp = ctx["_kms_crypto"]
        key = await sd.load_key(
            kid=p["kid"],
            version=p.get("version"),
            require_private=True,
            tenant=auth_tenant_from_ctx(ctx),
        )
        ct = AEADCiphertext(
            kid=p["kid"],
            version=p.get("version") or key.version,
            alg=p.get("alg") or "",
            nonce=b64d(p["nonce_b64"]),
            ct=b64d(p["ciphertext_b64"]),
            tag=b64d(p["tag_b64"]),
            aad=b64d_optional(p.get("aad_b64")),
        )
        pt = await cp.decrypt(key, ct, aad=ct.aad)
        return {"kid": key.kid, "version": key.version, "plaintext_b64": b64e(pt)}

    @op_ctx(alias="wrap", arity="member", persist="skip", returns="raw")
    async def wrap(self, *, ctx, db, request, payload):
        from ..utils import b64e, b64d_optional, auth_tenant_from_ctx

        p = self._params(ctx)
        sd = ctx["_kms_secrets"]
        cp = ctx["_kms_crypto"]
        kek = await sd.load_key(
            kid=p["kid"],
            version=p.get("version"),
            require_private=True,
            tenant=auth_tenant_from_ctx(ctx),
        )
        wrapped = await cp.wrap(
            kek,
            dek=b64d_optional(p.get("dek_b64")),
            wrap_alg=p.get("wrap_alg"),
            nonce=b64d_optional(p.get("nonce_b64")),
        )
        return {
            "kek_kid": wrapped.kek_kid,
            "kek_version": wrapped.kek_version,
            "wrap_alg": wrapped.wrap_alg,
            "wrapped_b64": b64e(wrapped.wrapped),
            **({"nonce_b64": b64e(wrapped.nonce)} if wrapped.nonce else {}),
        }

    @op_ctx(alias="unwrap", arity="member", persist="skip", returns="raw")
    async def unwrap(self, *, ctx, db, request, payload):
        from ..utils import b64e, b64d, b64d_optional, auth_tenant_from_ctx

        p = self._params(ctx)
        sd = ctx["_kms_secrets"]
        cp = ctx["_kms_crypto"]
        kek = await sd.load_key(
            kid=p["kid"],
            version=p.get("version"),
            require_private=True,
            tenant=auth_tenant_from_ctx(ctx),
        )
        wrapped = WrappedKey(
            kek_kid=kek.kid,
            kek_version=kek.version,
            wrap_alg=p.get("wrap_alg") or "",
            nonce=b64d_optional(p.get("nonce_b64")),
            wrapped=b64d(p["wrapped_b64"]),
        )
        dek = await cp.unwrap(kek, wrapped)
        return {"kek_kid": kek.kid, "kek_version": kek.version, "dek_b64": b64e(dek)}

    @op_ctx(alias="encrypt_for_many", arity="member", persist="skip", returns="raw")
    async def encrypt_for_many(self, *, ctx, db, request, payload):
        from ..utils import b64e, b64d, b64d_optional, auth_tenant_from_ctx

        p = self._params(ctx)
        sd = ctx["_kms_secrets"]
        cp = ctx["_kms_crypto"]
        t = auth_tenant_from_ctx(ctx)
        recs = []
        for r in p.get("recipients", []):
            recs.append(
                await sd.load_key(
                    kid=r["kid"],
                    version=r.get("version"),
                    require_private=False,
                    tenant=t,
                )
            )
        env = await cp.encrypt_for_many(
            recs,
            b64d(p["plaintext_b64"]),
            enc_alg=p.get("enc_alg"),
            recipient_wrap_alg=p.get("recipient_wrap_alg"),
            aad=b64d_optional(p.get("aad_b64")),
            nonce=b64d_optional(p.get("nonce_b64")),
        )
        return {
            "enc_alg": env.enc_alg,
            "nonce_b64": b64e(env.nonce),
            "ciphertext_b64": b64e(env.ct),
            "tag_b64": b64e(env.tag),
            "recipients": [
                {
                    "kid": ri.kid,
                    "version": ri.version,
                    "wrap_alg": ri.wrap_alg,
                    "wrapped_key_b64": b64e(ri.wrapped_key),
                    **({"nonce_b64": b64e(ri.nonce)} if ri.nonce else {}),
                }
                for ri in env.recipients
            ],
            **({"aad_b64": b64e(env.aad)} if env.aad else {}),
        }
