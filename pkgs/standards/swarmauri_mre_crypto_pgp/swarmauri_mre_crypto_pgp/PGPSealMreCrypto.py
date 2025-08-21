"""OpenPGP sealed-per-recipient MRE provider."""

from __future__ import annotations

import base64
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from swarmauri_core.mre_crypto.types import MultiRecipientEnvelope, RecipientId, MreMode
from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_base.mre_crypto.MreCryptoBase import MreCryptoBase
from swarmauri_base.ComponentBase import ComponentBase

try:  # pragma: no cover - dependency optional at runtime
    import pgpy  # type: ignore

    _PGP_OK = True
except Exception:  # pragma: no cover
    _PGP_OK = False


def _ensure_pgpy() -> None:
    if not _PGP_OK:  # pragma: no cover - env dependent
        raise RuntimeError(
            "PGPSealMreCrypto requires 'PGPy'. Install with: pip install pgpy"
        )


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
    """Encrypt bytes for a recipient using OpenPGP."""
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


def _make_sealed_recipient(rid: str, sealed_payload: bytes) -> Dict[str, Any]:
    return {"id": rid, "sealed": sealed_payload}


@ComponentBase.register_type(MreCryptoBase, "PGPSealMreCrypto")
class PGPSealMreCrypto(MreCryptoBase):
    """OpenPGP sealed-per-recipient MRE provider."""

    type: str = "PGPSealMreCrypto"

    def supports(self) -> Dict[str, Iterable[str | MreMode]]:
        return {
            "recipient": ("OpenPGP-SEAL",),
            "modes": (MreMode.SEALED_PER_RECIPIENT,),
            "features": (),
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
            except Exception as e:  # pragma: no cover - best effort
                last_err = e
                continue
        raise last_err or PermissionError(
            "None of the provided identities could open the envelope."
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
