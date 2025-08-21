"""PGPSealMreCrypto: IMreCrypto provider (sealed-per-recipient, OpenPGP).
Mode
----
- sealed_per_recipient (ONLY)
  For each recipient:
    • PGP-encrypt the *payload itself* (sealed payload per recipient)
  There is NO shared AEAD payload and NO AAD binding in this mode.
Out of scope
------------
- Signing: use swarmauri_core.signing.ISigning implementations.
- Header-only “wrap DEK for many”: use IMreWrap mix-in if you need it.

KeyRef expectations
-------------------
Public recipients (encrypt):
  - {"kind":"pgpy_pub", "pub": pgpy.PGPKey}
  - {"kind":"pgpy_pub_armored", "pub": "<ASCII armored PUBLIC key>"}

Private identities (open/rewrap):
  - {"kind":"pgpy_priv", "priv": pgpy.PGPKey}    (unlocked or unlockable via opts["passphrase"])
  - {"kind":"pgpy_priv_armored", "priv": "<ASCII armored PRIVATE key>"}

Options (opts)
--------------
- For private keys locked with a passphrase: opts["passphrase"] = str|bytes
- For rewrap(add=...): requires the *plaintext* via opts["plaintext"] = bytes
  (because payload is sealed per recipient; we must reseal the plaintext)

Dependencies
------------
- PGP: pip install pgpy
"""

from __future__ import annotations

import base64
from swarmauri_base.mre_crypto.MreCryptoBase import MreCryptoBase
from typing import Dict, Iterable, Mapping, Optional, Sequence, Any, List, Literal

from swarmauri_core.mre_crypto.types import MultiRecipientEnvelope, RecipientId, MreMode
from swarmauri_core.crypto.types import Alg, KeyRef

# ----- external deps -----
try:
    import pgpy

    _PGP_OK = True
except Exception:  # pragma: no cover - dependency check
    _PGP_OK = False


def _ensure_pgpy() -> None:
    if not _PGP_OK:  # pragma: no cover - simple guard
        raise RuntimeError(
            "PGPSealMreCrypto requires 'PGPy'. Install with: pip install pgpy"
        )


# ============================== Helpers (PGP) ==============================


def _load_pubkey(ref: KeyRef) -> "pgpy.PGPKey":
    _ensure_pgpy()
    if isinstance(ref, dict):
        kind = ref.get("kind")
        if kind == "pgpy_pub" and isinstance(ref.get("pub"), pgpy.PGPKey):
            return ref["pub"]
        if kind == "pgpy_pub_armored" and isinstance(ref.get("pub"), str):
            k, _ = pgpy.PGPKey.from_blob(ref["pub"])
            return k
    raise TypeError("Unsupported recipient KeyRef for PGP public key.")


def _load_privkey(ref: KeyRef, passphrase: Optional[bytes | str]) -> "pgpy.PGPKey":
    _ensure_pgpy()
    if isinstance(ref, dict):
        kind = ref.get("kind")
        if kind == "pgpy_priv" and isinstance(ref.get("priv"), pgpy.PGPKey):
            k: pgpy.PGPKey = ref["priv"]
        elif kind == "pgpy_priv_armored" and isinstance(ref.get("priv"), str):
            k, _ = pgpy.PGPKey.from_blob(ref["priv"])
        else:
            raise TypeError("Unsupported identity KeyRef for PGP private key.")
        if not k.is_unlocked:
            if passphrase is None:
                raise RuntimeError(
                    "PGP private key is locked; supply opts['passphrase']."
                )
            k.unlock(passphrase)
        return k
    raise TypeError("Unsupported identity KeyRef for PGP private key.")


def _fingerprint_pub(k: "pgpy.PGPKey") -> str:
    return str(k.fingerprint)


def _pgp_encrypt_bytes_for(pub: "pgpy.PGPKey", data: bytes) -> bytes:
    """
    PGPy often treats message payloads as text. To ensure byte fidelity, base64-encode
    before encrypting, and decode after decrypting.
    """
    _ensure_pgpy()
    msg = pgpy.PGPMessage.new(base64.b64encode(data), file=False)
    enc = pub.encrypt(msg)
    return bytes(enc.__bytes__())


def _pgp_decrypt_bytes_with(priv: "pgpy.PGPKey", blob: bytes) -> bytes:
    _ensure_pgpy()
    msg = pgpy.PGPMessage.from_blob(blob)
    dec = priv.decrypt(msg)
    if isinstance(dec.message, str):
        return base64.b64decode(dec.message.encode("utf-8"))
    return base64.b64decode(dec.message)


# ============================== Envelope shapers ==============================


def _make_sealed_recipient(rid: str, sealed_payload: bytes) -> Dict[str, Any]:
    return {"id": rid, "sealed": sealed_payload}


# ============================== Provider ==============================


class PGPSealMreCrypto(MreCryptoBase):
    type: Literal["PGPSealMreCrypto"] = "PGPSealMreCrypto"
    """
    OpenPGP sealed-per-recipient MRE provider.

    - Supports:
        • MreMode.SEALED_PER_RECIPIENT (ONLY)
    - Recipient protection: OpenPGP-SEAL
    - No shared AEAD payload; no AAD.
    """

    def supports(self) -> Dict[str, Iterable[str | MreMode]]:
        return {
            "recipient": ("OpenPGP-SEAL",),
            "modes": (MreMode.SEALED_PER_RECIPIENT,),
            "features": (),
        }

    # ————— Encrypt (N) —————
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
        _ensure_pgpy()

        m = (
            MreMode(mode)
            if isinstance(mode, str)
            else (mode or MreMode.SEALED_PER_RECIPIENT)
        )
        if m != MreMode.SEALED_PER_RECIPIENT:
            raise ValueError(
                f"PGPSealMreCrypto supports only mode={MreMode.SEALED_PER_RECIPIENT.value}."
            )
        if aad is not None:
            raise ValueError("AAD is not supported in sealed_per_recipient mode.")

        pubs = [_load_pubkey(r) for r in recipients]
        rids = [_fingerprint_pub(pk) for pk in pubs]

        sealed_entries = [
            _make_sealed_recipient(rid, _pgp_encrypt_bytes_for(pk, pt))
            for rid, pk in zip(rids, pubs)
        ]
        env: MultiRecipientEnvelope = {
            "mode": MreMode.SEALED_PER_RECIPIENT.value,
            "recipient_alg": "OpenPGP-SEAL",
            "payload": {"kind": "sealed_per_recipient"},
            "recipients": sealed_entries,
        }
        if shared:
            env["shared"] = dict(shared)
        return env

    # ————— Open (single) —————
    async def open_for(
        self,
        my_identity: KeyRef,
        env: MultiRecipientEnvelope,
        *,
        aad: Optional[bytes] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        _ensure_pgpy()
        if env.get("mode") != MreMode.SEALED_PER_RECIPIENT.value:
            raise ValueError("Envelope mode mismatch; expected sealed_per_recipient.")
        if aad is not None:
            raise ValueError("AAD is not supported in sealed_per_recipient mode.")

        priv = _load_privkey(my_identity, (opts or {}).get("passphrase"))
        my_id = str(priv.fingerprint)

        entries: List[Dict[str, Any]] = env.get("recipients", [])
        target = next((e for e in entries if e.get("id") == my_id), None)
        if target:
            return _pgp_decrypt_bytes_with(priv, target["sealed"])

        for e in entries:
            try:
                return _pgp_decrypt_bytes_with(priv, e["sealed"])
            except Exception:
                continue
        raise PermissionError("This identity cannot open the sealed envelope.")

    # ————— Open (many) —————
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
                continue
        raise last_err or PermissionError(
            "None of the provided identities could open the envelope."
        )

    # ————— Rewrap —————
    async def rewrap(
        self,
        env: MultiRecipientEnvelope,
        *,
        add: Optional[Sequence[KeyRef]] = None,
        remove: Optional[Sequence[RecipientId]] = None,
        recipient_alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> MultiRecipientEnvelope:
        _ensure_pgpy()
        if env.get("mode") != MreMode.SEALED_PER_RECIPIENT.value:
            raise ValueError("Envelope mode mismatch; expected sealed_per_recipient.")

        add = add or ()
        remove_ids = set(remove or ())

        new_env: MultiRecipientEnvelope = {k: v for k, v in env.items()}
        current_entries: List[Dict[str, Any]] = list(new_env.get("recipients", []))

        if remove_ids:
            current_entries = [
                e for e in current_entries if e.get("id") not in remove_ids
            ]

        if add:
            pt_bytes = (opts or {}).get("plaintext")
            if not isinstance(pt_bytes, (bytes, bytearray)):
                raise RuntimeError(
                    "Rewrap(add=...) in sealed_per_recipient mode requires opts['plaintext'] (bytes)."
                )
            pubs = [_load_pubkey(r) for r in add]
            rids = [_fingerprint_pub(pk) for pk in pubs]
            new_entries = [
                _make_sealed_recipient(rid, _pgp_encrypt_bytes_for(pk, pt_bytes))
                for rid, pk in zip(rids, pubs)
            ]
            remaining = [
                e for e in current_entries if e["id"] not in {rid for rid in rids}
            ]
            current_entries = remaining + new_entries

        new_env["recipients"] = current_entries
        return new_env
