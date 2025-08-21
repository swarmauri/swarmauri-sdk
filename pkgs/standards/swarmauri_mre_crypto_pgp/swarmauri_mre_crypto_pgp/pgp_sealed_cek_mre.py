"""PGPSealedCekMreCrypto

Multi-recipient encryption provider using a shared AEAD payload and OpenPGP
sealing of the content-encryption key (CEK).
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import os

from swarmauri_core.mre_crypto.IMreCrypto import IMreCrypto
from swarmauri_core.crypto.types import Alg, KeyRef

try:  # type-checking only
    from swarmauri_core.mre_crypto.types import MultiRecipientEnvelope, RecipientId
except Exception:  # pragma: no cover - typing fallback
    MultiRecipientEnvelope = Dict[str, Any]  # type: ignore
    RecipientId = str  # type: ignore

try:  # pragma: no cover - optional runtime dep
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    _CRYPTOGRAPHY_OK = True
except Exception:  # pragma: no cover
    _CRYPTOGRAPHY_OK = False

try:  # pragma: no cover - optional runtime dep
    import pgpy

    _PGP_OK = True
except Exception:  # pragma: no cover
    _PGP_OK = False


def _ensure_crypto() -> None:
    if not _CRYPTOGRAPHY_OK:
        raise RuntimeError(
            "PGPSealedCekMreCrypto requires 'cryptography'. Install with: pip install cryptography"
        )


def _ensure_pgpy() -> None:
    if not _PGP_OK:
        raise RuntimeError(
            "PGPSealedCekMreCrypto requires 'PGPy'. Install with: pip install pgpy"
        )


# ---------------------------------------------------------------------------
# PGP helpers
# ---------------------------------------------------------------------------


def _load_pgpy_pubkey(rec: KeyRef) -> Tuple[str, "pgpy.PGPKey"]:
    _ensure_pgpy()
    if isinstance(rec, dict):
        kind = rec.get("kind")
        if kind == "pgpy_pub" and isinstance(rec.get("pub"), pgpy.PGPKey):
            pk = rec["pub"]
        elif kind == "pgpy_key" and isinstance(rec.get("key"), pgpy.PGPKey):
            k = rec["key"]
            pk = k.pubkey if hasattr(k, "pubkey") else k
        elif kind == "pgpy_pub_armored" and isinstance(rec.get("pub"), str):
            pk, _ = pgpy.PGPKey.from_blob(rec["pub"])
        else:
            raise TypeError("Unsupported KeyRef for PGP public key encryption.")
    else:
        raise TypeError("Unsupported KeyRef type for PGP public key encryption.")

    if getattr(pk, "is_public", True) is False and hasattr(pk, "pubkey"):
        pk = pk.pubkey  # type: ignore[arg-type]

    rid = str(pk.fingerprint)
    return rid, pk


def _load_pgpy_privkey(
    my: KeyRef, *, passphrase: Optional[bytes | str]
) -> "pgpy.PGPKey":
    _ensure_pgpy()
    if isinstance(my, dict):
        kind = my.get("kind")
        if kind == "pgpy_key" and isinstance(my.get("key"), pgpy.PGPKey):
            k = my["key"]
        elif kind == "pgpy_key_armored" and isinstance(my.get("key"), str):
            k, _ = pgpy.PGPKey.from_blob(my["key"])
        else:
            raise TypeError("Unsupported KeyRef for PGP private key.")
    else:
        raise TypeError("Unsupported KeyRef for PGP private key.")

    if getattr(k, "is_unlocked", True) is False:
        if passphrase is None:
            raise RuntimeError("PGP private key is locked. Provide opts['passphrase'].")
        k.unlock(passphrase)
    return k


# ---------------------------------------------------------------------------
# AEAD helpers
# ---------------------------------------------------------------------------


def _aead_encrypt(
    cek: bytes, pt: bytes, *, aad: Optional[bytes]
) -> Tuple[bytes, bytes, bytes]:
    _ensure_crypto()
    if len(cek) not in (16, 24, 32):
        raise ValueError("AES-GCM key must be 16/24/32 bytes.")
    nonce = os.urandom(12)
    aead = AESGCM(cek)
    ct_plus_tag = aead.encrypt(nonce, pt, aad)
    tag = ct_plus_tag[-16:]
    ct = ct_plus_tag[:-16]
    return nonce, ct, tag


def _aead_decrypt(
    cek: bytes, nonce: bytes, ct: bytes, tag: bytes, *, aad: Optional[bytes]
) -> bytes:
    _ensure_crypto()
    aead = AESGCM(cek)
    return aead.decrypt(nonce, ct + tag, aad)


class PGPSealedCekMreCrypto(IMreCrypto):
    """IMreCrypto provider for the ``sealed_cek+aead`` mode using OpenPGP."""

    def supports(self) -> Dict[str, Iterable[str]]:  # pragma: no cover - trivial
        return {
            "payload": ("AES-256-GCM",),
            "recipient": ("OpenPGP-SEAL",),
            "modes": ("sealed_cek+aead",),
            "features": ("aad", "rewrap_without_reencrypt"),
        }

    async def encrypt_for_many(
        self,
        recipients: Sequence[KeyRef],
        pt: bytes,
        *,
        payload_alg: Optional[Alg] = None,
        recipient_alg: Optional[Alg] = None,
        mode: Optional[str] = None,
        aad: Optional[bytes] = None,
        shared: Optional[Mapping[str, bytes]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> MultiRecipientEnvelope:
        mode = mode or "sealed_cek+aead"
        if mode != "sealed_cek+aead":
            raise ValueError(
                "PGPSealedCekMreCrypto only supports mode='sealed_cek+aead'."
            )
        payload_alg = payload_alg or "AES-256-GCM"
        if payload_alg != "AES-256-GCM":
            raise ValueError("Unsupported payload_alg for PGPSealedCekMreCrypto.")
        recipient_alg = recipient_alg or "OpenPGP-SEAL"
        if recipient_alg != "OpenPGP-SEAL":
            raise ValueError(
                "Unsupported recipient_alg for PGPSealedCekMreCrypto (expected 'OpenPGP-SEAL')."
            )
        if not recipients:
            raise ValueError("At least one recipient is required.")

        cek = os.urandom(32)
        nonce, ct, tag = _aead_encrypt(cek, pt, aad=aad)

        _ensure_pgpy()
        rec_headers: List[Dict[str, Any]] = []
        for rec in recipients:
            rid, pub = _load_pgpy_pubkey(rec)
            literal = pgpy.PGPMessage.new(cek, file=False)
            enc = pub.encrypt(literal)
            header_bytes = bytes(enc.__bytes__())
            rec_headers.append({"id": rid, "header": header_bytes})

        env: MultiRecipientEnvelope = {
            "mode": "sealed_cek+aead",
            "payload": {
                "kind": "aead",
                "alg": payload_alg,
                "nonce": nonce,
                "ct": ct,
                "tag": tag,
                "aad": aad,
            },
            "recipient_alg": recipient_alg,
            "recipients": rec_headers,
            "shared": dict(shared) if shared else None,
            "version": 1,
        }
        return env

    async def open_for(
        self,
        my_identity: KeyRef,
        env: MultiRecipientEnvelope,
        *,
        aad: Optional[bytes] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        if env.get("mode") != "sealed_cek+aead":
            raise ValueError("Unsupported envelope mode.")
        payload = env.get("payload") or {}
        if not isinstance(payload, dict) or payload.get("kind") != "aead":
            raise ValueError("Malformed envelope payload for sealed_cek+aead.")
        nonce: bytes = payload["nonce"]
        ct: bytes = payload["ct"]
        tag: bytes = payload["tag"]
        bound_aad = payload.get("aad", None)
        if (
            (aad is not None)
            and (bound_aad is not None)
            and (bytes(aad) != bytes(bound_aad))
        ):
            raise ValueError("AAD mismatch.")

        passphrase = None
        if opts and "passphrase" in opts:
            passphrase = opts["passphrase"]
        priv = _load_pgpy_privkey(my_identity, passphrase=passphrase)
        my_rid = str((priv.pubkey if hasattr(priv, "pubkey") else priv).fingerprint)

        header = None
        for ent in env.get("recipients") or []:
            if ent.get("id") == my_rid:
                header = ent.get("header")
                break
        if not isinstance(header, (bytes, bytearray)):
            raise ValueError("Recipient not found in envelope.")

        sealed = pgpy.PGPMessage.from_blob(bytes(header))
        lit = priv.decrypt(sealed)
        cek = bytes(lit.message)
        return _aead_decrypt(cek, nonce, ct, tag, aad=bound_aad)

    async def open_for_many(
        self,
        my_identities: Sequence[KeyRef],
        env: MultiRecipientEnvelope,
        *,
        aad: Optional[bytes] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        last_err: Optional[Exception] = None
        for kid in my_identities:
            try:
                return await self.open_for(kid, env, aad=aad, opts=opts)
            except Exception as e:  # pragma: no cover - best effort
                last_err = e
                continue
        raise (
            last_err
            if last_err
            else RuntimeError("Failed to open envelope with provided identities.")
        )

    async def rewrap(
        self,
        env: MultiRecipientEnvelope,
        *,
        add: Optional[Sequence[KeyRef]] = None,
        remove: Optional[Sequence[RecipientId]] = None,
        recipient_alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> MultiRecipientEnvelope:
        if env.get("mode") != "sealed_cek+aead":
            raise ValueError("Unsupported envelope mode for rewrap.")
        if recipient_alg and recipient_alg != "OpenPGP-SEAL":
            raise ValueError(
                "PGPSealedCekMreCrypto only supports recipient_alg='OpenPGP-SEAL' in rewrap."
            )

        add = add or []
        remove_ids = set(remove or [])
        recipients = list(env.get("recipients") or [])
        payload = env.get("payload") or {}
        rotate_flag = bool((opts or {}).get("rotate_payload_on_revoke")) and bool(
            remove_ids
        )

        cek: Optional[bytes] = None
        need_cek = add or rotate_flag
        if need_cek:
            if opts and isinstance(opts.get("cek"), (bytes, bytearray)):
                cek = bytes(opts["cek"])
            else:
                opener_list = (opts or {}).get("opener_identities")
                if not opener_list:
                    raise RuntimeError(
                        "Rewrap(add=... or rotate) requires opts['cek'] or opts['opener_identities']."
                    )
                if not isinstance(opener_list, (list, tuple)):
                    opener_list = [opener_list]
                passphrase = (opts or {}).get("passphrase")
                for ident in opener_list:
                    try:
                        priv = _load_pgpy_privkey(ident, passphrase=passphrase)
                        for ent in recipients:
                            try:
                                sealed = pgpy.PGPMessage.from_blob(bytes(ent["header"]))
                                with priv:
                                    lit = priv.decrypt(sealed)
                                cek = bytes(lit.message)
                                break
                            except Exception:
                                continue
                        if cek:
                            break
                    except Exception:
                        continue
            if cek is None:
                raise RuntimeError("Unable to recover CEK for rewrap.")

        if remove_ids:
            recipients = [r for r in recipients if r.get("id") not in remove_ids]

        if rotate_flag and cek is not None:
            new_cek = os.urandom(32)
            bound_aad = payload.get("aad")
            pt = _aead_decrypt(
                cek, payload["nonce"], payload["ct"], payload["tag"], aad=bound_aad
            )
            nonce, ct, tag = _aead_encrypt(new_cek, pt, aad=bound_aad)
            env["payload"] = {
                "kind": "aead",
                "alg": payload.get("alg", "AES-256-GCM"),
                "nonce": nonce,
                "ct": ct,
                "tag": tag,
                "aad": bound_aad,
            }
            cek = new_cek
            recipients = []

        for rec in add:
            rid, pub = _load_pgpy_pubkey(rec)
            literal = pgpy.PGPMessage.new(cek, file=False)
            enc = pub.encrypt(literal)
            header_bytes = bytes(enc.__bytes__())
            recipients = [r for r in recipients if r.get("id") != rid]
            recipients.append({"id": rid, "header": header_bytes})

        env["recipients"] = recipients
        return env
