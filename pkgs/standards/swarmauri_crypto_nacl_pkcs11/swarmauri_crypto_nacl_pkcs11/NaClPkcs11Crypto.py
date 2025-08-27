"""NaCl + PKCS#11 backed crypto provider with sealing support."""

from __future__ import annotations

import json
import os
import base64
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional, Tuple, Literal

from nacl.public import PublicKey, PrivateKey, SealedBox
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import pkcs11
from pkcs11 import Attribute, KeyType as PKKeyType, Mechanism

from swarmauri_core.crypto.types import (
    AEADCiphertext,
    Alg,
    KeyRef,
    MultiRecipientEnvelope,
    RecipientInfo,
    WrappedKey,
    UnsupportedAlgorithm,
)
from swarmauri_core.crypto.types import KeyType
from swarmauri_base.crypto.CryptoBase import CryptoBase
from swarmauri_base.ComponentBase import ComponentBase


@dataclass
class _Resolved:
    kind: str
    material: bytes | Any


def _resolve_keyref_for_aead(key: KeyRef) -> _Resolved:
    if key.type == KeyType.SYMMETRIC and key.material:
        kb = key.material
        if len(kb) not in (16, 24, 32):
            raise ValueError("AES key must be 128/192/256 bits")
        return _Resolved(kind="aes", material=kb)
    raise ValueError("Unsupported KeyRef for AEAD")


def _resolve_keyref_for_sealed_box(key: KeyRef, private: bool = False) -> _Resolved:
    if not private:
        if key.type == KeyType.X25519 and key.public:
            return _Resolved(kind="x25519_pub", material=key.public)
    else:
        if key.type == KeyType.X25519 and key.material:
            return _Resolved(kind="x25519_priv", material=key.material)
    raise ValueError("Unsupported KeyRef for sealed-box")


def _resolve_keyref_for_hsm_kek(kek: KeyRef) -> Tuple[pkcs11.Session, pkcs11.SecretKey]:
    tags = kek.tags or {}
    module_path = tags.get("module") or os.environ.get("PKCS11_MODULE")
    slot_label = tags.get("slot_label") or os.environ.get("PKCS11_SLOT_LABEL")
    user_pin = tags.get("user_pin") or os.environ.get("PKCS11_USER_PIN")
    kek_label = tags.get("label") or os.environ.get("PKCS11_KEK_LABEL", "autokms-kek")

    lib = pkcs11.lib(module_path)
    token = next(t for t in lib.get_tokens() if t.label == slot_label)
    sess = token.open(user_pin=user_pin)
    keys = list(
        sess.get_objects(
            {
                Attribute.LABEL: kek_label,
                Attribute.CLASS: pkcs11.constants.ObjectClass.SECRET_KEY,
            }
        )
    )
    if not keys:
        raise RuntimeError(f"KEK '{kek_label}' not found in slot {slot_label}")
    return sess, keys[0]


_SEAL_ALG = "X25519-SEALEDBOX"
_AEAD_ALG = "AES-GCM"
_WRAP_ALG = "AES-KW"


@ComponentBase.register_type(CryptoBase, "NaClPkcs11Crypto")
class NaClPkcs11Crypto(CryptoBase):
    """Concrete implementation of the ICrypto contract using PyNaCl and PKCS#11."""

    type: Literal["NaClPkcs11Crypto"] = "NaClPkcs11Crypto"

    def supports(self) -> Dict[str, Iterable[Alg]]:
        return {
            "encrypt": (_AEAD_ALG,),
            "decrypt": (_AEAD_ALG,),
            "wrap": (_WRAP_ALG,),
            "unwrap": (_WRAP_ALG,),
            "seal": (_SEAL_ALG,),
            "unseal": (_SEAL_ALG,),
            "for_many": (_SEAL_ALG,),
        }

    # ────────────────────────── AEAD ──────────────────────────
    async def encrypt(
        self,
        key: KeyRef,
        pt: bytes,
        *,
        alg: Optional[Alg] = None,
        aad: Optional[bytes] = None,
        nonce: Optional[bytes] = None,
    ) -> AEADCiphertext:
        alg = alg or _AEAD_ALG
        if alg != _AEAD_ALG:
            raise UnsupportedAlgorithm(f"Unsupported AEAD algorithm: {alg}")
        r = _resolve_keyref_for_aead(key)
        n = nonce or os.urandom(12)
        aead = AESGCM(r.material)
        ct_with_tag = aead.encrypt(n, pt, aad)
        ct, tag = ct_with_tag[:-16], ct_with_tag[-16:]
        return AEADCiphertext(
            kid=key.kid,
            version=key.version,
            alg=alg,
            nonce=n,
            ct=ct,
            tag=tag,
            aad=aad,
        )

    async def decrypt(
        self,
        key: KeyRef,
        ct: AEADCiphertext,
        *,
        aad: Optional[bytes] = None,
    ) -> bytes:
        if ct.alg != _AEAD_ALG:
            raise UnsupportedAlgorithm(f"Unsupported AEAD algorithm: {ct.alg}")
        r = _resolve_keyref_for_aead(key)
        aead = AESGCM(r.material)
        blob = ct.ct + ct.tag
        return aead.decrypt(ct.nonce, blob, aad or ct.aad)

    # ────────────────────────── Sign / Verify ──────────────────────────
    # ────────────────────────── Wrap / Unwrap ──────────────────────────
    async def wrap(
        self,
        kek: KeyRef,
        *,
        dek: Optional[bytes] = None,
        wrap_alg: Optional[Alg] = None,
        nonce: Optional[bytes] = None,
        aad: Optional[bytes] = None,
    ) -> WrappedKey:
        alg = wrap_alg or _WRAP_ALG
        if alg != _WRAP_ALG:
            raise UnsupportedAlgorithm(f"Unsupported wrap algorithm: {alg}")
        if not dek:
            raise ValueError("wrap requires a DEK")
        sess, kek_obj = _resolve_keyref_for_hsm_kek(kek)
        tmp = sess.create_secret_key(PKKeyType.AES, len(dek) * 8, value=dek)
        wrapped = kek_obj.wrap_key(tmp, mechanism=Mechanism.AES_KEY_WRAP_PAD)
        tmp.destroy()
        return WrappedKey(
            kek_kid=kek.kid, kek_version=kek.version, wrap_alg=alg, wrapped=wrapped
        )

    async def unwrap(self, kek: KeyRef, wrapped: WrappedKey) -> bytes:
        if wrapped.wrap_alg != _WRAP_ALG:
            raise UnsupportedAlgorithm(
                f"Unsupported wrapped key algorithm: {wrapped.wrap_alg}"
            )
        sess, kek_obj = _resolve_keyref_for_hsm_kek(kek)
        key = kek_obj.unwrap_key(
            wrapped.wrapped,
            mechanism=Mechanism.AES_KEY_WRAP_PAD,
            template={
                Attribute.CLASS: pkcs11.ObjectClass.SECRET_KEY,
                Attribute.KEY_TYPE: PKKeyType.AES,
            },
        )
        return key[Attribute.VALUE]

    # ────────────────── Multi-recipient (Sealed Box) ──────────────────
    async def encrypt_for_many(
        self,
        recipients: Iterable[KeyRef],
        pt: bytes,
        *,
        enc_alg: Optional[Alg] = None,
        recipient_wrap_alg: Optional[Alg] = None,
        aad: Optional[bytes] = None,
        nonce: Optional[bytes] = None,
    ) -> MultiRecipientEnvelope:
        alg = enc_alg or _SEAL_ALG
        if alg != _SEAL_ALG:
            raise UnsupportedAlgorithm(f"Unsupported multi-recipient alg: {alg}")

        infos = []
        for ref in recipients:
            r = _resolve_keyref_for_sealed_box(ref, private=False)
            c = SealedBox(PublicKey(r.material)).encrypt(pt)
            infos.append(
                RecipientInfo(
                    kid=ref.kid,
                    version=ref.version,
                    wrap_alg=_SEAL_ALG,
                    wrapped_key=c,
                )
            )

        # optional AAD binding by wrapping whole envelope
        if aad:
            dek = AESGCM.generate_key(bit_length=256)
            aead = AESGCM(dek)
            n = os.urandom(12)
            packed = json.dumps(
                {i.kid: base64.b64encode(i.wrapped_key).decode("ascii") for i in infos}
            ).encode("utf-8")
            ct_with_tag = aead.encrypt(n, packed, aad)
            ct, tag = ct_with_tag[:-16], ct_with_tag[-16:]
            # The DEK is not returned; caller should wrap it separately if needed.
            return MultiRecipientEnvelope(
                enc_alg=_AEAD_ALG,
                nonce=n,
                ct=ct,
                tag=tag,
                recipients=tuple(infos),
                aad=aad,
            )

        return MultiRecipientEnvelope(
            enc_alg=_SEAL_ALG,
            nonce=b"",
            ct=b"",
            tag=b"",
            recipients=tuple(infos),
            aad=None,
        )

    # ───────────────────────────── seal / unseal ─────────────────────────────
    async def seal(
        self,
        recipient: KeyRef,
        pt: bytes,
        *,
        alg: Optional[Alg] = None,
    ) -> bytes:
        alg = alg or _SEAL_ALG
        if alg != _SEAL_ALG:
            raise UnsupportedAlgorithm(f"Unsupported seal algorithm: {alg}")
        r = _resolve_keyref_for_sealed_box(recipient, private=False)
        return SealedBox(PublicKey(r.material)).encrypt(pt)

    async def unseal(
        self,
        recipient_priv: KeyRef,
        sealed: bytes,
        *,
        alg: Optional[Alg] = None,
    ) -> bytes:
        alg = alg or _SEAL_ALG
        if alg != _SEAL_ALG:
            raise UnsupportedAlgorithm(f"Unsupported seal algorithm: {alg}")
        r = _resolve_keyref_for_sealed_box(recipient_priv, private=True)
        return SealedBox(PrivateKey(r.material)).decrypt(sealed)
