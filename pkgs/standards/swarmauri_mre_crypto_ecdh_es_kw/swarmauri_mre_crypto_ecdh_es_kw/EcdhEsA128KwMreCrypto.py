from __future__ import annotations

import os
from typing import Dict, Iterable, Mapping, Optional, Sequence

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.keywrap import aes_key_unwrap, aes_key_wrap

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.mre_crypto.MreCryptoBase import MreCryptoBase
from swarmauri_core.crypto.types import (
    Alg,
    KeyRef,
    RecipientInfo,
    MultiRecipientEnvelope,
)
from swarmauri_core.mre_crypto.types import MreMode, RecipientId


def _pub_from_keyref(ref: KeyRef) -> ec.EllipticCurvePublicKey:
    if isinstance(ref, dict):
        obj = ref.get("obj")
        if ref.get("kind") == "cryptography_obj" and isinstance(
            obj, ec.EllipticCurvePublicKey
        ):
            return obj
    if hasattr(ref, "public") and isinstance(ref.public, bytes):
        return ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), ref.public)
    raise TypeError("Unsupported KeyRef for EC public key")


def _priv_from_keyref(ref: KeyRef) -> ec.EllipticCurvePrivateKey:
    if isinstance(ref, dict):
        obj = ref.get("obj")
        if ref.get("kind") == "cryptography_obj" and isinstance(
            obj, ec.EllipticCurvePrivateKey
        ):
            return obj
    if hasattr(ref, "material") and isinstance(ref.material, bytes):
        return serialization.load_pem_private_key(ref.material, password=None)
    raise TypeError("Unsupported KeyRef for EC private key")


def _kid(ref: KeyRef) -> str:
    if isinstance(ref, dict):
        return str(ref.get("kid", ""))
    return ref.kid


def _version(ref: KeyRef) -> int:
    if isinstance(ref, dict):
        return int(ref.get("version", 1))
    return ref.version


def _kdf(shared: bytes, salt: bytes, info: bytes) -> bytes:
    hkdf = HKDF(algorithm=hashes.SHA256(), length=16, salt=salt, info=info)
    return hkdf.derive(shared)


@ComponentBase.register_type(MreCryptoBase, "EcdhEsA128KwMreCrypto")
class EcdhEsA128KwMreCrypto(MreCryptoBase):
    """MRE provider using ECDH-ES key agreement and AES-128-KW."""

    type: str = "EcdhEsA128KwMreCrypto"

    def supports(self) -> Dict[str, Iterable[str | MreMode]]:
        return {
            "payload": ("A128GCM",),
            "recipient": ("ECDH-ES+A128KW",),
            "modes": (MreMode.ENC_ONCE_HEADERS,),
            "features": ("aad",),
        }

    async def encrypt_for_many(
        self,
        recipients: Sequence[KeyRef],
        pt: bytes,
        *,
        payload_alg: Optional[Alg] = None,
        recipient_alg: Optional[Alg] = None,
        mode: Optional[MreMode | str] = None,
        aad: Optional[bytes] = None,
        shared: Optional[Mapping[str, bytes]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> MultiRecipientEnvelope:
        if payload_alg not in (None, "A128GCM"):
            raise ValueError("Only payload_alg='A128GCM' supported")
        if recipient_alg not in (None, "ECDH-ES+A128KW"):
            raise ValueError("Only recipient_alg='ECDH-ES+A128KW' supported")
        cek = os.urandom(16)
        nonce = os.urandom(12)
        aead = AESGCM(cek)
        ct_with_tag = aead.encrypt(nonce, pt, aad)
        ct, tag = ct_with_tag[:-16], ct_with_tag[-16:]
        recip_infos: list[RecipientInfo] = []
        for ref in recipients:
            pub = _pub_from_keyref(ref)
            eph_sk = ec.generate_private_key(ec.SECP256R1())
            shared_secret = eph_sk.exchange(ec.ECDH(), pub)
            pub_bytes = pub.public_bytes(
                encoding=serialization.Encoding.X962,
                format=serialization.PublicFormat.UncompressedPoint,
            )
            eph_pub_bytes = eph_sk.public_key().public_bytes(
                encoding=serialization.Encoding.X962,
                format=serialization.PublicFormat.UncompressedPoint,
            )
            kek = _kdf(shared_secret, salt=pub_bytes, info=eph_pub_bytes)
            wrapped = aes_key_wrap(kek, cek)
            recip_infos.append(
                RecipientInfo(
                    kid=_kid(ref),
                    version=_version(ref),
                    wrap_alg="ECDH-ES+A128KW",
                    wrapped_key=wrapped,
                    nonce=eph_pub_bytes,
                )
            )
        return MultiRecipientEnvelope(
            enc_alg="A128GCM",
            nonce=nonce,
            ct=ct,
            tag=tag,
            recipients=tuple(recip_infos),
            aad=aad,
        )

    async def open_for(
        self,
        my_identity: KeyRef,
        env: MultiRecipientEnvelope,
        *,
        aad: Optional[bytes] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        priv = _priv_from_keyref(my_identity)
        my_pub_bytes = priv.public_key().public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint,
        )
        for r in env.recipients:
            if r.wrap_alg != "ECDH-ES+A128KW":
                continue
            eph_pub = ec.EllipticCurvePublicKey.from_encoded_point(
                ec.SECP256R1(),
                r.nonce or b"",
            )
            shared_secret = priv.exchange(ec.ECDH(), eph_pub)
            kek = _kdf(shared_secret, salt=my_pub_bytes, info=r.nonce or b"")
            try:
                cek = aes_key_unwrap(kek, r.wrapped_key)
            except Exception:
                continue
            aead = AESGCM(cek)
            return aead.decrypt(env.nonce, env.ct + env.tag, aad)
        raise ValueError("No matching recipient for provided identity")

    async def open_for_many(
        self,
        my_identities: Sequence[KeyRef],
        env: MultiRecipientEnvelope,
        *,
        aad: Optional[bytes] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        last_err: Optional[Exception] = None
        for ident in my_identities:
            try:
                return await self.open_for(ident, env, aad=aad, opts=opts)
            except Exception as e:
                last_err = e
        if last_err:
            raise last_err
        raise ValueError("No identities provided")

    async def rewrap(
        self,
        env: MultiRecipientEnvelope,
        *,
        add: Optional[Sequence[KeyRef]] = None,
        remove: Optional[Sequence[RecipientId]] = None,
        recipient_alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> MultiRecipientEnvelope:
        raise ValueError("Rewrap not supported")
