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

try:  # Kyber768 support for hybrid mode (optional dependency)
    from pqcrypto.kem import kyber768

    _HAVE_KYBER768 = True
except Exception:  # pragma: no cover - optional dependency may be absent
    kyber768 = None  # type: ignore[assignment]
    _HAVE_KYBER768 = False

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


def _fingerprint_hybrid(pk: X25519PublicKey, mlkem_pk: bytes) -> str:
    data = _pub_bytes(pk) + bytes(mlkem_pk)
    return hashlib.sha256(data).hexdigest()


_MAGIC = b"AGE-MRE-X25519\x00"
_VERSION = b"\x01"
_HYBRID_MAGIC = b"AGE-MRE-X25519MLKEM768\x00"
_HYBRID_VERSION = b"\x01"
_NONCE_LEN = 12
_KEY_LEN = 32
_RECIPIENT_ALG_X25519 = "X25519-SEAL"
_RECIPIENT_ALG_HYBRID = "X25519MLKEM768-SEAL"


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


def _coerce_bytes(value: object, label: str) -> bytes:
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    raise TypeError(f"{label} must be raw bytes for hybrid mode.")


def _hybrid_pub_from_keyref(ref: KeyRef) -> tuple[X25519PublicKey, bytes]:
    if isinstance(ref, dict):
        kind = ref.get("kind")
        if kind == "hybrid_x25519_mlkem768":
            x_ref = ref.get("x25519")
            mlkem_pk = ref.get("mlkem_pk") or ref.get("mlkem768_pk")
            if x_ref is None or mlkem_pk is None:
                raise TypeError("Hybrid recipient requires 'x25519' and 'mlkem_pk'.")
            return _pub_from_keyref(x_ref), _coerce_bytes(mlkem_pk, "mlkem_pk")
    raise TypeError("Unsupported KeyRef for hybrid public key material.")


def _hybrid_priv_from_keyref(ref: KeyRef) -> tuple[X25519PrivateKey, bytes, bytes]:
    if isinstance(ref, dict):
        kind = ref.get("kind")
        if kind == "hybrid_x25519_mlkem768":
            x_ref = ref.get("x25519")
            mlkem_sk = ref.get("mlkem_sk") or ref.get("mlkem768_sk")
            mlkem_pk = ref.get("mlkem_pk") or ref.get("mlkem768_pk")
            if x_ref is None or mlkem_sk is None or mlkem_pk is None:
                raise TypeError(
                    "Hybrid identity requires 'x25519', 'mlkem_sk', and 'mlkem_pk'."
                )
            return (
                _priv_from_keyref(x_ref),
                _coerce_bytes(mlkem_sk, "mlkem_sk"),
                _coerce_bytes(mlkem_pk, "mlkem_pk"),
            )
    raise TypeError("Unsupported KeyRef for hybrid private key material.")


def _seal_hybrid_x25519_mlkem768(
    pt: bytes, recipient_pk: X25519PublicKey, mlkem_pk: bytes
) -> bytes:
    if not _HAVE_KYBER768:
        raise RuntimeError("pqcrypto.kyber768 is required for hybrid sealing.")
    eph_sk = X25519PrivateKey.generate()
    eph_pk = eph_sk.public_key()
    shared_x = eph_sk.exchange(recipient_pk)
    pqc_ct, pqc_shared = kyber768.encrypt(mlkem_pk)
    salt = _pub_bytes(recipient_pk) + mlkem_pk
    info = _HYBRID_MAGIC + _pub_bytes(eph_pk) + pqc_ct
    combined = shared_x + pqc_shared
    key = _hkdf_key(combined, salt=salt, info=info, length=_KEY_LEN)
    aead = ChaCha20Poly1305(key)
    nonce = os.urandom(_NONCE_LEN)
    ct = aead.encrypt(nonce, pt, _HYBRID_MAGIC)
    pqc_len = len(pqc_ct).to_bytes(2, "big")
    return b"".join(
        [_HYBRID_MAGIC, _HYBRID_VERSION, _pub_bytes(eph_pk), pqc_len, pqc_ct, nonce, ct]
    )


def _unseal_hybrid_x25519_mlkem768(
    sk: X25519PrivateKey, mlkem_sk: bytes, mlkem_pk: bytes, sealed: bytes
) -> bytes:
    if (
        not sealed.startswith(_HYBRID_MAGIC)
        or len(sealed) < len(_HYBRID_MAGIC) + 1 + 32 + 2 + _NONCE_LEN + 16
    ):
        raise ValueError("Malformed hybrid sealed blob.")
    off = len(_HYBRID_MAGIC)
    v = sealed[off : off + 1]
    off += 1
    if v != _HYBRID_VERSION:
        raise ValueError("Unsupported hybrid sealed blob version.")
    eph_pk_b = sealed[off : off + 32]
    off += 32
    pqc_len = int.from_bytes(sealed[off : off + 2], "big")
    off += 2
    pqc_ct = sealed[off : off + pqc_len]
    off += pqc_len
    nonce = sealed[off : off + _NONCE_LEN]
    off += _NONCE_LEN
    ct = sealed[off:]
    eph_pk = X25519PublicKey.from_public_bytes(eph_pk_b)
    shared_x = sk.exchange(eph_pk)
    if not _HAVE_KYBER768:
        raise RuntimeError("pqcrypto.kyber768 is required for hybrid unsealing.")
    pqc_shared = kyber768.decrypt(mlkem_sk, pqc_ct)
    salt = _pub_bytes(sk.public_key()) + mlkem_pk
    info = _HYBRID_MAGIC + eph_pk_b + pqc_ct
    combined = shared_x + pqc_shared
    key = _hkdf_key(combined, salt=salt, info=info, length=_KEY_LEN)
    aead = ChaCha20Poly1305(key)
    return aead.decrypt(nonce, ct, _HYBRID_MAGIC)


class AgeMreCrypto(MreCryptoBase):
    """AgeMreCrypto (sealed-per-recipient, X25519 stanzas)."""

    type: str = "AgeMreCrypto"

    def supports(self) -> Dict[str, Iterable[str]]:
        modes = ("sealed_per_recipient",)
        return {
            "recipient": (_RECIPIENT_ALG_X25519, _RECIPIENT_ALG_HYBRID),
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
        recipient_alg = recipient_alg or _RECIPIENT_ALG_X25519
        if recipient_alg not in (_RECIPIENT_ALG_X25519, _RECIPIENT_ALG_HYBRID):
            raise ValueError(
                "AgeMreCrypto supports recipient_alg 'X25519-SEAL' or 'X25519MLKEM768-SEAL'."
            )
        recs: List[Dict[str, Any]] = []
        if recipient_alg == _RECIPIENT_ALG_X25519:
            for ref in recipients:
                pk = _pub_from_keyref(ref)
                sealed = _seal_x25519(pt, pk)
                rid = _fingerprint(pk)
                recs.append({"id": rid, "header": sealed})
        else:
            for ref in recipients:
                pk, mlkem_pk = _hybrid_pub_from_keyref(ref)
                sealed = _seal_hybrid_x25519_mlkem768(pt, pk, mlkem_pk)
                rid = _fingerprint_hybrid(pk, mlkem_pk)
                recs.append({"id": rid, "header": sealed, "mlkem_pk": mlkem_pk})
        env: MultiRecipientEnvelope = {
            "mode": m,
            "payload": {"kind": "sealed_per_recipient"},
            "recipient_alg": recipient_alg,
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
        recip_alg = env.get("recipient_alg") or _RECIPIENT_ALG_X25519
        if recip_alg not in (_RECIPIENT_ALG_X25519, _RECIPIENT_ALG_HYBRID):
            raise ValueError(
                "Envelope recipient_alg must be 'X25519-SEAL' or 'X25519MLKEM768-SEAL'"
            )
        recipients = env.get("recipients", [])
        if recip_alg == _RECIPIENT_ALG_X25519:
            sk = _priv_from_keyref(my_identity)
            my_rid = _fingerprint(sk.public_key())
            for r in recipients:
                if r.get("id") == my_rid:
                    sealed = r.get("header")
                    if not isinstance(sealed, (bytes, bytearray)):
                        raise ValueError("Recipient header is not bytes.")
                    return _unseal_x25519(sk, sealed)
            for r in recipients:
                sealed = r.get("header")
                if not isinstance(sealed, (bytes, bytearray)):
                    continue
                try:
                    return _unseal_x25519(sk, sealed)
                except Exception:
                    continue
            raise ValueError("This identity cannot open the envelope.")
        sk, mlkem_sk, mlkem_pk = _hybrid_priv_from_keyref(my_identity)
        my_pk = sk.public_key()
        my_rid = _fingerprint_hybrid(my_pk, mlkem_pk)
        for r in recipients:
            sealed = r.get("header")
            if not isinstance(sealed, (bytes, bytearray)):
                continue
            mlkem_entry = r.get("mlkem_pk")
            mlkem_entry_b = (
                _coerce_bytes(mlkem_entry, "mlkem_pk")
                if isinstance(mlkem_entry, (bytes, bytearray))
                else mlkem_pk
            )
            rid_match = r.get("id")
            if rid_match == my_rid:
                return _unseal_hybrid_x25519_mlkem768(
                    sk, mlkem_sk, mlkem_entry_b, bytes(sealed)
                )
            # attempt recompute fingerprint if envelope carried alternate ML-KEM key
            try:
                candidate_rid = _fingerprint_hybrid(my_pk, mlkem_entry_b)
            except Exception:
                candidate_rid = None
            if candidate_rid == rid_match:
                return _unseal_hybrid_x25519_mlkem768(
                    sk, mlkem_sk, mlkem_entry_b, bytes(sealed)
                )
            try:
                return _unseal_hybrid_x25519_mlkem768(
                    sk, mlkem_sk, mlkem_entry_b, bytes(sealed)
                )
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
        recipient_alg = (
            recipient_alg or env.get("recipient_alg") or _RECIPIENT_ALG_X25519
        )
        if recipient_alg not in (_RECIPIENT_ALG_X25519, _RECIPIENT_ALG_HYBRID):
            raise ValueError(
                "AgeMreCrypto supports recipient_alg 'X25519-SEAL' or 'X25519MLKEM768-SEAL'."
            )
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
                if recipient_alg == _RECIPIENT_ALG_X25519:
                    pk = _pub_from_keyref(ref)
                    sealed = _seal_x25519(plaintext, pk)
                    rid = _fingerprint(pk)
                    recipients_list.append({"id": rid, "header": sealed})
                else:
                    pk, mlkem_pk = _hybrid_pub_from_keyref(ref)
                    sealed = _seal_hybrid_x25519_mlkem768(plaintext, pk, mlkem_pk)
                    rid = _fingerprint_hybrid(pk, mlkem_pk)
                    recipients_list.append(
                        {"id": rid, "header": sealed, "mlkem_pk": mlkem_pk}
                    )
        updated: MultiRecipientEnvelope = {
            "mode": "sealed_per_recipient",
            "payload": {"kind": "sealed_per_recipient"},
            "recipient_alg": recipient_alg,
            "recipients": recipients_list,
        }
        if "shared" in env:
            updated["shared"] = env["shared"]
        return updated
