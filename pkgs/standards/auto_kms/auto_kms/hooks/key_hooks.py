from __future__ import annotations

from typing import Any, Mapping

from autoapi.v2 import Phase
from swarmauri_core.crypto.types import AEADCiphertext, WrappedKey
from ..utils import (
    params,
    b64e,
    b64d,
    b64d_optional,
    coerce_key_type_from_params,
    coerce_uses_from_params,
    coerce_export_policy,
    auth_tenant_from_ctx,
    asdict_desc,
)


def register_key_hooks(api) -> None:
    def _params(ctx) -> Mapping[str, Any]:
        return params(ctx)

    @api.register_hook(Phase.PRE_HANDLER, model="Key", op="create")
    async def _h_key_create(ctx):
        # Example: create via secrets driver
        p = _params(ctx)
        sd = ctx["_kms_secrets"]
        desc = await sd.store_key(
            key_type=coerce_key_type_from_params(p),
            uses=coerce_uses_from_params(p),
            name=p.get("name"),
            material=None,
            export_policy=coerce_export_policy(p.get("export_policy")),
            tags=p.get("tags"),
        )
        ctx["__kms_result__"] = asdict_desc(desc)

    @api.register_hook(Phase.PRE_HANDLER, model="Key", op="rotate")
    async def _h_key_rotate(ctx):
        p = _params(ctx)
        sd = ctx["_kms_secrets"]
        desc = await sd.rotate(
            kid=p["kid"],
            material=None,
            make_primary=bool(p.get("make_primary", True)),
            tags=p.get("tags"),
            tenant=auth_tenant_from_ctx(ctx),
        )
        ctx["__kms_result__"] = asdict_desc(desc)

    @api.register_hook(Phase.PRE_HANDLER, model="Key", op="disable")
    async def _h_key_disable(ctx):
        p = _params(ctx)
        sd = ctx["_kms_secrets"]
        desc = await sd.set_state(
            kid=p["kid"], state="disabled", tenant=auth_tenant_from_ctx(ctx)
        )
        ctx["__kms_result__"] = asdict_desc(desc)

    @api.register_hook(Phase.PRE_HANDLER, model="Key", op="encrypt")
    async def _h_key_encrypt(ctx):
        p = _params(ctx)
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
        ctx["__kms_result__"] = {
            "kid": ct.kid,
            "version": ct.version,
            "alg": ct.alg,
            "nonce_b64": b64e(ct.nonce),
            "ciphertext_b64": b64e(ct.ct),
            "tag_b64": b64e(ct.tag),
            **({"aad_b64": b64e(ct.aad)} if ct.aad else {}),
        }

    @api.register_hook(Phase.PRE_HANDLER, model="Key", op="decrypt")
    async def _h_key_decrypt(ctx):
        p = _params(ctx)
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
        ctx["__kms_result__"] = {
            "kid": key.kid,
            "version": key.version,
            "plaintext_b64": b64e(pt),
        }

    @api.register_hook(Phase.PRE_HANDLER, model="Key", op="wrap")
    async def _h_key_wrap(ctx):
        p = _params(ctx)
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
        ctx["__kms_result__"] = {
            "kek_kid": wrapped.kek_kid,
            "kek_version": wrapped.kek_version,
            "wrap_alg": wrapped.wrap_alg,
            "wrapped_b64": b64e(wrapped.wrapped),
            **({"nonce_b64": b64e(wrapped.nonce)} if wrapped.nonce else {}),
        }

    @api.register_hook(Phase.PRE_HANDLER, model="Key", op="unwrap")
    async def _h_key_unwrap(ctx):
        p = _params(ctx)
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
        ctx["__kms_result__"] = {
            "kek_kid": kek.kid,
            "kek_version": kek.version,
            "dek_b64": b64e(dek),
        }

    @api.register_hook(Phase.PRE_HANDLER, model="Key", op="encrypt_for_many")
    async def _h_key_encrypt_for_many(ctx):
        p = _params(ctx)
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
        ctx["__kms_result__"] = {
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
