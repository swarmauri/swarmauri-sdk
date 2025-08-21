"""PGPMreCrypto: OpenPGP-backed MRE provider supporting multiple modes."""

from __future__ import annotations

import base64
import os
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)

from swarmauri_core.mre_crypto.types import MultiRecipientEnvelope, RecipientId, MreMode
from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_base.mre_crypto.MreCryptoBase import MreCryptoBase
from swarmauri_base.ComponentBase import ComponentBase

try:  # pragma: no cover - dependency optional at runtime
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    _CRYPTOGRAPHY_OK = True
except Exception:  # pragma: no cover
    _CRYPTOGRAPHY_OK = False

try:  # pragma: no cover - dependency optional at runtime
    import pgpy

    _PGP_OK = True
except Exception:  # pragma: no cover
    _PGP_OK = False


def _ensure_crypto() -> None:
    if not _CRYPTOGRAPHY_OK:
        raise RuntimeError(
            "PGPMreCrypto requires 'cryptography'. Install with: pip install cryptography"
        )


def _ensure_pgpy() -> None:
    if not _PGP_OK:
        raise RuntimeError(
            "PGPMreCrypto requires 'PGPy'. Install with: pip install pgpy"
        )


# ---------------------------------------------------------------------------
# PGP helpers
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# AEAD helpers
# ---------------------------------------------------------------------------


def _aead_encrypt_gcm(
    cek: bytes, pt: bytes, *, aad: Optional[bytes]
) -> Tuple[bytes, bytes, bytes]:
    _ensure_crypto()
    if len(cek) != 32:
        raise ValueError("AES-256-GCM requires a 32-byte CEK.")
    aead = AESGCM(cek)
    nonce = os.urandom(12)
    cttag = aead.encrypt(nonce, pt, aad)
    return nonce, cttag[:-16], cttag[-16:]


def _aead_decrypt_gcm(
    cek: bytes, nonce: bytes, ct: bytes, tag: bytes, *, aad: Optional[bytes]
) -> bytes:
    _ensure_crypto()
    aead = AESGCM(cek)
    return aead.decrypt(nonce, ct + tag, aad)


def _make_aead_payload(
    payload_alg: str, nonce: bytes, ct: bytes, tag: bytes, aad: Optional[bytes]
) -> Dict[str, Any]:
    return {
        "kind": "aead",
        "alg": payload_alg,
        "nonce": nonce,
        "ct": ct,
        "tag": tag,
        "aad": aad,
    }


def _make_recipient_header(rid: str, header: bytes) -> Dict[str, Any]:
    return {"id": rid, "header": header}


def _make_sealed_recipient(rid: str, sealed_payload: bytes) -> Dict[str, Any]:
    return {"id": rid, "sealed": sealed_payload}


@ComponentBase.register_type(MreCryptoBase, "PGPMreCrypto")
class PGPMreCrypto(MreCryptoBase):
    """OpenPGP-backed multi-recipient encryption provider."""

    type: Literal["PGPMreCrypto"] = "PGPMreCrypto"
    default_payload_alg: str = "AES-256-GCM"
    default_recipient_alg: str = "OpenPGP"

    def supports(
        self,
    ) -> Dict[str, Iterable[str | MreMode]]:  # pragma: no cover - trivial
        modes: Tuple[str | MreMode, ...] = (
            MreMode.ENC_ONCE_HEADERS,
            MreMode.SEALED_PER_RECIPIENT,
        )
        return {
            "payload": (self.default_payload_alg,),
            "recipient": ("OpenPGP", "OpenPGP-SEAL"),
            "modes": modes,
            "features": ("aad", "rewrap_without_reencrypt"),
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
            else (mode or MreMode.ENC_ONCE_HEADERS)
        )
        payload_alg = payload_alg or self.default_payload_alg
        recipient_alg = recipient_alg or self.default_recipient_alg

        pubs = [_load_pubkey(r) for r in recipients]
        rids = [_fingerprint_pub(pk) for pk in pubs]

        if m == MreMode.ENC_ONCE_HEADERS:
            if payload_alg != "AES-256-GCM":
                raise ValueError(
                    "PGPMreCrypto currently supports only AES-256-GCM for shared payload."
                )
            cek = os.urandom(32)
            nonce, ct, tag = _aead_encrypt_gcm(cek, pt, aad=aad)
            headers = [
                _make_recipient_header(rid, _pgp_encrypt_bytes_for(pk, cek))
                for rid, pk in zip(rids, pubs)
            ]
            env: MultiRecipientEnvelope = {
                "mode": MreMode.ENC_ONCE_HEADERS.value,
                "payload_alg": payload_alg,
                "recipient_alg": "OpenPGP",
                "payload": _make_aead_payload(payload_alg, nonce, ct, tag, aad),
                "recipients": headers,
            }
            if shared:
                env["shared"] = dict(shared)
            return env

        if m == MreMode.SEALED_PER_RECIPIENT:
            sealed_entries = [
                _make_sealed_recipient(rid, _pgp_encrypt_bytes_for(pk, pt))
                for rid, pk in zip(rids, pubs)
            ]
            env = {
                "mode": MreMode.SEALED_PER_RECIPIENT.value,
                "recipient_alg": "OpenPGP-SEAL",
                "payload": {"kind": "sealed_per_recipient"},
                "recipients": sealed_entries,
            }
            if shared:
                env["shared"] = dict(shared)
            return env

        raise ValueError(f"Unsupported mode: {mode}")

    async def open_for(
        self,
        my_identity: KeyRef,
        env: MultiRecipientEnvelope,
        *,
        aad: Optional[bytes] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        _ensure_pgpy()
        mode_str = env.get("mode")
        m = MreMode(mode_str) if isinstance(mode_str, str) else mode_str
        priv = _load_privkey(my_identity, (opts or {}).get("passphrase"))

        if m == MreMode.ENC_ONCE_HEADERS:
            my_id = str(priv.fingerprint)
            headers: List[Dict[str, Any]] = env.get("recipients", [])
            target = next((h for h in headers if h.get("id") == my_id), None)

            cek: Optional[bytes] = None
            if target:
                cek = _pgp_decrypt_bytes_with(priv, target["header"])
            else:
                for h in headers:
                    try:
                        cek = _pgp_decrypt_bytes_with(priv, h["header"])
                        break
                    except Exception:
                        continue
            if cek is None:
                raise PermissionError("This identity cannot open the envelope.")

            payload = env["payload"]
            if payload.get("alg") != "AES-256-GCM":
                raise ValueError("Unsupported payload_alg for PGPMreCrypto open.")
            nonce, ct, tag = payload["nonce"], payload["ct"], payload["tag"]
            bound_aad = payload.get("aad", None)
            if aad is not None and bound_aad is not None and aad != bound_aad:
                raise ValueError("AAD mismatch.")
            return _aead_decrypt_gcm(cek, nonce, ct, tag, aad=bound_aad)

        if m == MreMode.SEALED_PER_RECIPIENT:
            my_id = str(priv.fingerprint)
            entries: List[Dict[str, Any]] = env.get("recipients", [])
            target = next((e for e in entries if e.get("id") == my_id), None)
            if not target:
                for e in entries:
                    try:
                        return _pgp_decrypt_bytes_with(priv, e["sealed"])
                    except Exception:
                        continue
                raise PermissionError("This identity cannot open the sealed envelope.")
            return _pgp_decrypt_bytes_with(priv, target["sealed"])

        raise ValueError(f"Unsupported mode: {mode_str}")

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
            except Exception as e:  # pragma: no cover
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
        mode_str = env.get("mode")
        m = MreMode(mode_str) if isinstance(mode_str, str) else mode_str

        add = add or ()
        remove_ids = set(remove or ())

        new_env: MultiRecipientEnvelope = {k: v for k, v in env.items()}

        if m == MreMode.ENC_ONCE_HEADERS:
            current_headers: List[Dict[str, Any]] = list(new_env.get("recipients", []))
            if remove_ids:
                current_headers = [
                    h for h in current_headers if h.get("id") not in remove_ids
                ]

            cek: Optional[bytes] = None
            if add:
                if opts and isinstance(opts.get("cek"), (bytes, bytearray)):
                    cek = bytes(opts["cek"])
                elif opts and opts.get("manage_key"):
                    manage_key = _load_privkey(
                        opts["manage_key"], (opts or {}).get("passphrase")
                    )
                    candidate_headers = current_headers or list(
                        env.get("recipients", [])
                    )
                    for h in candidate_headers:
                        try:
                            cek = _pgp_decrypt_bytes_with(manage_key, h["header"])
                            break
                        except Exception:
                            continue
                else:
                    raise RuntimeError(
                        "Rewrap(add=...) requires opts['cek'] or opts['manage_key']."
                    )

            if add and cek is not None:
                pubs = [_load_pubkey(r) for r in add]
                rids = [_fingerprint_pub(pk) for pk in pubs]
                new_headers = [
                    _make_recipient_header(rid, _pgp_encrypt_bytes_for(pk, cek))
                    for rid, pk in zip(rids, pubs)
                ]
                merged: List[Dict[str, Any]] = []
                for h in current_headers:
                    if h["id"] not in {rid for rid in rids}:
                        merged.append(h)
                merged.extend(new_headers)
                current_headers = merged

            rotate = bool(opts.get("rotate_payload_on_revoke")) if opts else False
            if remove_ids and rotate:
                if not cek:
                    if opts and opts.get("manage_key"):
                        manage_key = _load_privkey(
                            opts["manage_key"], (opts or {}).get("passphrase")
                        )
                        for h in env.get("recipients", []):
                            try:
                                cek = _pgp_decrypt_bytes_with(manage_key, h["header"])
                                break
                            except Exception:
                                continue
                    if not cek:
                        raise RuntimeError(
                            "rotate_payload_on_revoke requires CEK via opts['manage_key'] or opts['cek']."
                        )

                new_cek = os.urandom(32)
                payload = env["payload"]
                old_pt = _aead_decrypt_gcm(
                    cek,
                    payload["nonce"],
                    payload["ct"],
                    payload["tag"],
                    aad=payload.get("aad"),
                )
                nonce, ct, tag = _aead_encrypt_gcm(
                    new_cek, old_pt, aad=payload.get("aad")
                )
                new_env["payload"] = _make_aead_payload(
                    env.get("payload_alg", self.default_payload_alg),
                    nonce,
                    ct,
                    tag,
                    payload.get("aad"),
                )

                add_pubkeys = (opts or {}).get("add_pubkeys")
                if not isinstance(add_pubkeys, (list, tuple)) or not add_pubkeys:
                    raise RuntimeError(
                        "After rotation, provide opts['add_pubkeys'] = [KeyRef(pub=...), ...] for remaining recipients."
                    )
                pubs = [_load_pubkey(r) for r in add_pubkeys]
                rids = [_fingerprint_pub(pk) for pk in pubs]
                new_headers = [
                    _make_recipient_header(rid, _pgp_encrypt_bytes_for(pk, new_cek))
                    for rid, pk in zip(rids, pubs)
                ]
                current_headers = new_headers

            new_env["recipients"] = current_headers
            return new_env

        if m == MreMode.SEALED_PER_RECIPIENT:
            current_entries: List[Dict[str, Any]] = list(new_env.get("recipients", []))
            if remove_ids:
                current_entries = [
                    e for e in current_entries if e.get("id") not in remove_ids
                ]
            if add:
                pt_bytes = (opts or {}).get("plaintext")
                if not isinstance(pt_bytes, (bytes, bytearray)):
                    raise RuntimeError(
                        "Rewrap(add=...) in sealed_per_recipient mode requires opts['plaintext']."
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

        raise ValueError(f"Unsupported mode for rewrap: {mode_str}")
