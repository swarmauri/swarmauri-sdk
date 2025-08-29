from __future__ import annotations

import hashlib
import os
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Union

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import serialization

from swarmauri_base.mre_crypto.MreCryptoBase import MreCryptoBase
from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_core.mre_crypto.types import MultiRecipientEnvelope, RecipientId

try:  # Optional enum import; string fallback for portability.
    _HAVE_MREMODE = True
except Exception:  # pragma: no cover
    _HAVE_MREMODE = False


# ---------------------------------------------------------------------------
# helper functions
# ---------------------------------------------------------------------------


def _mode_token(value: Optional[Union[str, Any]] = None) -> str:
    """Normalize a mode token to str. Default to sealed_per_recipient."""
    if value is None:
        return "sealed_per_recipient"
    if _HAVE_MREMODE and hasattr(value, "value"):
        return str(value.value)
    return str(value)


def _pub_from_keyref(ref: KeyRef) -> X25519PublicKey:
    """Extract an X25519 public key from a KeyRef."""
    if isinstance(ref, dict):
        kind = ref.get("kind")
        if kind == "cryptography_obj" and isinstance(ref.get("obj"), X25519PublicKey):
            return ref["obj"]  # type: ignore[return-value]
        if kind in ("raw_x25519_pk", "age_x25519_pk"):
            b = ref.get("bytes")
            if isinstance(b, (bytes, bytearray)) and len(b) == 32:
                return X25519PublicKey.from_public_bytes(bytes(b))
    raise TypeError("Unsupported KeyRef for X25519 public key.")


def _priv_from_keyref(ref: KeyRef) -> X25519PrivateKey:
    """Extract an X25519 private key from a KeyRef."""
    if isinstance(ref, dict):
        kind = ref.get("kind")
        if kind == "cryptography_obj" and isinstance(ref.get("obj"), X25519PrivateKey):
            return ref["obj"]  # type: ignore[return-value]
        if kind in ("raw_x25519_sk", "age_x25519_sk"):
            b = ref.get("bytes")
            if isinstance(b, (bytes, bytearray)) and len(b) == 32:
                return X25519PrivateKey.from_private_bytes(bytes(b))
    raise TypeError("Unsupported KeyRef for X25519 private key.")


def _pub_bytes(pk: X25519PublicKey) -> bytes:
    return pk.public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
    )


def _fingerprint(pk: X25519PublicKey) -> str:
    return hashlib.sha256(_pub_bytes(pk)).hexdigest()


_MAGIC = b"AGE-MRE-X25519\x00"
_VERSION = b"\x01"
_NONCE_LEN = 12
_KEY_LEN = 32


def _hkdf_key(
    shared_secret: bytes, salt: bytes, info: bytes, length: int = 32
) -> bytes:
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        info=info,
    )
    return hkdf.derive(shared_secret)


def _seal_x25519(pt: bytes, recipient_pk: X25519PublicKey) -> bytes:
    eph_sk = X25519PrivateKey.generate()
    eph_pk = eph_sk.public_key()
    shared = eph_sk.exchange(recipient_pk)
    salt = _pub_bytes(recipient_pk)
    info = _MAGIC + _pub_bytes(eph_pk)
    key = _hkdf_key(shared, salt=salt, info=info, length=_KEY_LEN)
    aead = ChaCha20Poly1305(key)
    nonce = os.urandom(_NONCE_LEN)
    ct = aead.encrypt(nonce, pt, _MAGIC)
    return b"".join([_MAGIC, _VERSION, _pub_bytes(eph_pk), nonce, ct])


def _unseal_x25519(sk: X25519PrivateKey, sealed: bytes) -> bytes:
    if (
        not sealed.startswith(_MAGIC)
        or len(sealed) < len(_MAGIC) + 1 + 32 + _NONCE_LEN + 16
    ):
        raise ValueError("Malformed sealed blob.")
    off = len(_MAGIC)
    v = sealed[off : off + 1]
    off += 1
    if v != _VERSION:
        raise ValueError("Unsupported sealed blob version.")
    eph_pk_b = sealed[off : off + 32]
    off += 32
    nonce = sealed[off : off + _NONCE_LEN]
    off += _NONCE_LEN
    ct = sealed[off:]
    eph_pk = X25519PublicKey.from_public_bytes(eph_pk_b)
    shared = sk.exchange(eph_pk)
    my_pub = sk.public_key()
    salt = _pub_bytes(my_pub)
    info = _MAGIC + eph_pk_b
    key = _hkdf_key(shared, salt=salt, info=info, length=_KEY_LEN)
    aead = ChaCha20Poly1305(key)
    return aead.decrypt(nonce, ct, _MAGIC)


class AgeMreCrypto(MreCryptoBase):
    """AgeMreCrypto (sealed-per-recipient, X25519 stanzas)."""

    type: str = "AgeMreCrypto"

    def supports(self) -> Dict[str, Iterable[str]]:
        modes = ("sealed_per_recipient",)
        return {
            "recipient": ("X25519-SEAL",),
            "modes": modes,
            "features": (),
        }

    async def encrypt_for_many(
        self,
        recipients: Sequence[KeyRef],
        pt: bytes,
        *,
        payload_alg: Optional[Alg] = None,
        recipient_alg: Optional[Alg] = None,
        mode: Optional[Union[str, Any]] = None,
        aad: Optional[bytes] = None,
        shared: Optional[Mapping[str, bytes]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> MultiRecipientEnvelope:
        m = _mode_token(mode)
        if m != "sealed_per_recipient":
            raise ValueError("AgeMreCrypto supports only mode='sealed_per_recipient'.")
        if recipient_alg not in (None, "X25519-SEAL"):
            raise ValueError("AgeMreCrypto supports only recipient_alg='X25519-SEAL'.")
        recs: List[Dict[str, Any]] = []
        for ref in recipients:
            pk = _pub_from_keyref(ref)
            sealed = _seal_x25519(pt, pk)
            rid = _fingerprint(pk)
            recs.append({"id": rid, "header": sealed})
        env: MultiRecipientEnvelope = {
            "mode": m,
            "payload": {"kind": "sealed_per_recipient"},
            "recipient_alg": "X25519-SEAL",
            "recipients": recs,
        }
        if shared:
            env["shared"] = dict(shared)
        return env

    async def open_for(
        self,
        my_identity: KeyRef,
        env: MultiRecipientEnvelope,
        *,
        aad: Optional[bytes] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        mode = str(env.get("mode", ""))
        if mode != "sealed_per_recipient":
            raise ValueError(
                "Envelope mode is not 'sealed_per_recipient' for AgeMreCrypto."
            )
        recip_alg = env.get("recipient_alg")
        if recip_alg != "X25519-SEAL":
            raise ValueError(
                "Envelope recipient_alg must be 'X25519-SEAL' for AgeMreCrypto."
            )
        sk = _priv_from_keyref(my_identity)
        my_rid = _fingerprint(sk.public_key())
        for r in env.get("recipients", []):
            if r.get("id") == my_rid:
                sealed = r.get("header")
                if not isinstance(sealed, (bytes, bytearray)):
                    raise ValueError("Recipient header is not bytes.")
                return _unseal_x25519(sk, sealed)
        for r in env.get("recipients", []):
            sealed = r.get("header")
            if not isinstance(sealed, (bytes, bytearray)):
                continue
            try:
                return _unseal_x25519(sk, sealed)
            except Exception:
                continue
        raise ValueError("This identity cannot open the envelope.")

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
            except Exception as e:  # pragma: no cover - keep last error
                last_err = e
                continue
        raise last_err if last_err else ValueError("No identities provided.")

    async def rewrap(
        self,
        env: MultiRecipientEnvelope,
        *,
        add: Optional[Sequence[KeyRef]] = None,
        remove: Optional[Sequence[RecipientId]] = None,
        recipient_alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> MultiRecipientEnvelope:
        mode = str(env.get("mode", ""))
        if mode != "sealed_per_recipient":
            raise ValueError(
                "Envelope mode is not 'sealed_per_recipient' for AgeMreCrypto."
            )
        if recipient_alg not in (None, "X25519-SEAL"):
            raise ValueError("AgeMreCrypto supports only recipient_alg='X25519-SEAL'.")
        recipients_list: List[Dict[str, Any]] = list(env.get("recipients", []))
        if remove:
            remove_set = set(remove)
            recipients_list = [
                r for r in recipients_list if r.get("id") not in remove_set
            ]
        plaintext: Optional[bytes] = None
        if add:
            if opts and isinstance(opts.get("pt"), (bytes, bytearray)):
                plaintext = bytes(opts["pt"])
            elif opts and opts.get("open_with") is not None:
                plaintext = await self.open_for(opts["open_with"], env)  # type: ignore[arg-type]
            else:
                raise ValueError(
                    "Adding recipients requires opts['pt'] or opts['open_with']."
                )
            for ref in add:
                pk = _pub_from_keyref(ref)
                sealed = _seal_x25519(plaintext, pk)
                rid = _fingerprint(pk)
                recipients_list.append({"id": rid, "header": sealed})
        updated: MultiRecipientEnvelope = {
            "mode": "sealed_per_recipient",
            "payload": {"kind": "sealed_per_recipient"},
            "recipient_alg": "X25519-SEAL",
            "recipients": recipients_list,
        }
        if "shared" in env:
            updated["shared"] = env["shared"]
        return updated
