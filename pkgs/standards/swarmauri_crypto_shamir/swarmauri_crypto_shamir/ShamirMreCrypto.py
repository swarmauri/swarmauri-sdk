"""Shamir-based Multi-Recipient Encryption provider."""

from __future__ import annotations

import os
import json
import hashlib
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Tuple, List, Union

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_core.mre_crypto.types import MultiRecipientEnvelope, RecipientId
from swarmauri_base.mre_crypto.MreCryptoBase import MreCryptoBase
from swarmauri_base.ComponentBase import ComponentBase


# ======================== Field and envelope constants ========================

# Prime field for Shamir (Mersenne prime > 2^521)
_P = (1 << 521) - 1
_ZERO = 0
_ONE = 1

# CEK size for AES-256-GCM
_CEK_LEN = 32
_NONCE_LEN = 12
_TAG_LEN = 16

# Envelope tokens
_MODE = "sealed_cek+aead"
_RECIP_ALG = "SHAMIR-KOFN"
_PAYLOAD_AEAD_DEFAULT = "AES-256-GCM"

# Header (per-recipient share) binary format
_HDR_MAGIC = b"SHAMIR-KOFN\x00"
_HDR_VER = b"\x01"


# ================================ utils ======================================


def _int_to_bytes(x: int) -> bytes:
    if x == 0:
        return b"\x00"
    length = (x.bit_length() + 7) // 8
    return x.to_bytes(length, "big")


def _bytes_to_int(b: bytes) -> int:
    return int.from_bytes(b, "big")


def _mod_inv(a: int, p: int) -> int:
    # Modular inverse via Fermat's little theorem; p is prime
    if a % p == 0:
        raise ZeroDivisionError("division by zero in modular inverse")
    return pow(a, p - 2, p)


def _poly_eval_at(x: int, coeffs: Sequence[int], p: int = _P) -> int:
    """
    Evaluate polynomial a0 + a1*x + a2*x^2 + ... at x (mod p).
    coeffs[0] is the secret (a0).
    """
    acc = 0
    power = 1
    for a in coeffs:
        acc = (acc + (a * power)) % p
        power = (power * x) % p
    return acc


def _lagrange_interpolate_at(
    x: int, points: Sequence[Tuple[int, int]], p: int = _P
) -> int:
    """
    Compute f(x) from k points (x_i, y_i) on a degree-(k-1) polynomial over GF(p).
    Works for x == 0 (reconstruct secret) or any other x (evaluate at new x).
    """
    k = len(points)
    xs = [xi for (xi, _) in points]
    ys = [yi for (_, yi) in points]
    total = 0
    for i in range(k):
        xi, yi = xs[i], ys[i]
        num = 1
        den = 1
        for j in range(k):
            if i == j:
                continue
            xj = xs[j]
            num = (num * (x - xj)) % p
            den = (den * (xi - xj)) % p
        li = (num * _mod_inv(den % p, p)) % p
        total = (total + (yi * li)) % p
    return total


def _encode_share(x: int, y: int) -> bytes:
    xb = _int_to_bytes(x)
    yb = _int_to_bytes(y)
    return b"".join(
        [
            _HDR_MAGIC,
            _HDR_VER,
            len(xb).to_bytes(2, "big"),
            xb,
            len(yb).to_bytes(2, "big"),
            yb,
        ]
    )


def _decode_share(b: bytes) -> Tuple[int, int]:
    if not b.startswith(_HDR_MAGIC):
        raise ValueError("Malformed Shamir header (magic).")
    off = len(_HDR_MAGIC)
    ver = b[off : off + 1]
    off += 1
    if ver != _HDR_VER:
        raise ValueError("Unsupported Shamir header version.")
    xlen = int.from_bytes(b[off : off + 2], "big")
    off += 2
    xb = b[off : off + xlen]
    off += xlen
    ylen = int.from_bytes(b[off : off + 2], "big")
    off += 2
    yb = b[off : off + ylen]
    if len(xb) != xlen or len(yb) != ylen:
        raise ValueError("Malformed Shamir header (length).")
    return (_bytes_to_int(xb), _bytes_to_int(yb))


def _sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def _stable_recipient_id(ref: KeyRef) -> str:
    """
    Produce a stable recipient id from a KeyRef without assuming key type.
    Preference:
      - explicit 'kid' or 'id' in dict
      - raw public bytes if available
      - canonicalized JSON of the dict
      - repr fallback
    """
    if isinstance(ref, dict):
        if "kid" in ref and isinstance(ref["kid"], (str, bytes)):
            v = ref["kid"]
            if isinstance(v, bytes):
                v = v.decode("utf-8", "ignore")
            return v
        if "id" in ref and isinstance(ref["id"], (str, bytes)):
            v = ref["id"]
            if isinstance(v, bytes):
                v = v.decode("utf-8", "ignore")
            return v
        obj = ref.get("obj")
        if hasattr(obj, "public_bytes"):
            try:
                pb = obj.public_bytes(encoding=None, format=None)  # type: ignore[arg-type]
                return hashlib.sha256(pb).hexdigest()
            except Exception:
                pass
        try:
            canon = json.dumps(
                ref, sort_keys=True, separators=(",", ":"), default=str
            ).encode("utf-8")
        except Exception:
            canon = repr(ref).encode("utf-8")
        return hashlib.sha256(canon).hexdigest()
    return hashlib.sha256(repr(ref).encode("utf-8")).hexdigest()


def _x_from_recipient_id(rid: str, used: set[int]) -> int:
    base = (
        int.from_bytes(_sha256(("SHAMIR-X|" + rid).encode("utf-8")), "big") % (_P - 1)
    ) + 1
    x = base
    while x in used:
        x = (x + 1) % _P
        if x == 0:
            x = 1
    used.add(x)
    return x


def _aes_gcm_encrypt(
    cek: bytes, pt: bytes, aad: Optional[bytes]
) -> Tuple[bytes, bytes, bytes]:
    nonce = os.urandom(_NONCE_LEN)
    enc = AESGCM(cek).encrypt(nonce, pt, aad)
    ct, tag = enc[:-_TAG_LEN], enc[-_TAG_LEN:]
    return nonce, ct, tag


def _aes_gcm_decrypt(
    cek: bytes, nonce: bytes, ct: bytes, tag: bytes, aad: Optional[bytes]
) -> bytes:
    return AESGCM(cek).decrypt(nonce, ct + tag, aad)


# ============================== implementation ===============================


@ComponentBase.register_type(MreCryptoBase, "ShamirMreCrypto")
class ShamirMreCrypto(MreCryptoBase):
    """Shamir secret sharing based MRE crypto provider."""

    type: str = "ShamirMreCrypto"

    def supports(self) -> Dict[str, Iterable[str]]:
        return {
            "payload": (_PAYLOAD_AEAD_DEFAULT,),
            "recipient": (_RECIP_ALG,),
            "modes": (_MODE,),
            "features": ("aad", "threshold", "rewrap_without_reencrypt"),
        }

    # ----------------------------- encrypt_for_many -----------------------------
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
        m = str(mode or _MODE)
        if m != _MODE:
            raise ValueError("ShamirMreCrypto supports only mode='sealed_cek+aead'.")
        if recipient_alg not in (None, _RECIP_ALG):
            raise ValueError(
                "ShamirMreCrypto supports only recipient_alg='SHAMIR-KOFN'."
            )
        palg = str(payload_alg or _PAYLOAD_AEAD_DEFAULT)
        if palg != _PAYLOAD_AEAD_DEFAULT:
            raise ValueError("ShamirMreCrypto supports only AES-256-GCM for now.")
        if not recipients:
            raise ValueError("At least one recipient is required.")
        n = len(recipients)
        k = int((opts or {}).get("threshold_k", (n // 2) + 1))
        k = max(1, min(k, n))
        cek = os.urandom(_CEK_LEN)
        nonce, ct, tag = _aes_gcm_encrypt(cek, pt, aad)
        secret = _bytes_to_int(cek)
        coeffs = [secret] + [
            int.from_bytes(os.urandom(64), "big") % _P for _ in range(max(0, k - 1))
        ]
        used_x: set[int] = set()
        rec_entries: List[Dict[str, Any]] = []
        for ref in recipients:
            rid = _stable_recipient_id(ref)
            x = _x_from_recipient_id(rid, used_x)
            y = _poly_eval_at(x, coeffs, _P)
            header = _encode_share(x, y)
            rec_entries.append({"id": rid, "header": header})
        payload = {
            "kind": "aead",
            "alg": palg,
            "nonce": nonce,
            "ct": ct,
            "tag": tag,
            "aad": aad,
        }
        env: MultiRecipientEnvelope = {
            "mode": _MODE,
            "payload": payload,
            "recipient_alg": _RECIP_ALG,
            "recipients": rec_entries,
            "shared": {
                "threshold_k": k.to_bytes(2, "big"),
                "cek_len": _CEK_LEN.to_bytes(2, "big"),
            },
        }
        if shared:
            extra = dict(shared)
            extra.pop("threshold_k", None)
            extra.pop("cek_len", None)
            env["shared"].update(extra)  # type: ignore[index]
        return env

    # --------------------------------- open_for --------------------------------
    async def open_for(
        self,
        my_identity: KeyRef,
        env: MultiRecipientEnvelope,
        *,
        aad: Optional[bytes] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        k = _decode_k(env)
        if k != 1:
            raise ValueError(
                "This envelope requires ≥2 shares; call open_for_many(...)."
            )
        rid = _stable_recipient_id(my_identity)
        share = _find_share_for(rid, env)
        if share is None:
            raise ValueError("This identity has no share in the envelope.")
        x, y = _decode_share(share)
        cek_int = y % _P
        cek = _int_to_bytes(cek_int).rjust(_decode_cek_len(env), b"\x00")
        payload = _expect_aead_payload(env)
        return _aes_gcm_decrypt(
            cek,
            payload["nonce"],
            payload["ct"],
            payload["tag"],
            aad or payload.get("aad"),
        )

    # ------------------------------- open_for_many ------------------------------
    async def open_for_many(
        self,
        my_identities: Sequence[KeyRef],
        env: MultiRecipientEnvelope,
        *,
        aad: Optional[bytes] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        if not my_identities:
            raise ValueError("No identities provided.")
        k = _decode_k(env)
        payload = _expect_aead_payload(env)
        points: List[Tuple[int, int]] = []
        seen_x: set[int] = set()
        for ident in my_identities:
            rid = _stable_recipient_id(ident)
            h = _find_share_for(rid, env)
            if h is None:
                continue
            x, y = _decode_share(h)
            if x in seen_x:
                continue
            seen_x.add(x)
            points.append((x, y))
            if len(points) >= k:
                break
        if len(points) < k:
            raise ValueError(
                f"Need at least {k} shares; provided {len(points)} that match the envelope."
            )
        cek_int = _lagrange_interpolate_at(0, points, _P)
        cek = _int_to_bytes(cek_int).rjust(_decode_cek_len(env), b"\x00")
        return _aes_gcm_decrypt(
            cek,
            payload["nonce"],
            payload["ct"],
            payload["tag"],
            aad or payload.get("aad"),
        )

    # ---------------------------------- rewrap ---------------------------------
    async def rewrap(
        self,
        env: MultiRecipientEnvelope,
        *,
        add: Optional[Sequence[KeyRef]] = None,
        remove: Optional[Sequence[RecipientId]] = None,
        recipient_alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> MultiRecipientEnvelope:
        if env.get("mode") != _MODE or env.get("recipient_alg") != _RECIP_ALG:
            raise ValueError("Envelope does not match ShamirMreCrypto mode/alg.")
        if recipient_alg not in (None, _RECIP_ALG):
            raise ValueError("recipient_alg must be SHAMIR-KOFN for ShamirMreCrypto.")
        k = _decode_k(env)
        cek_len = _decode_cek_len(env)
        recs: List[Dict[str, Any]] = list(env.get("recipients", []))
        if remove:
            to_remove = set(remove)
            recs = [r for r in recs if r.get("id") not in to_remove]
        rotate = (
            bool((opts or {}).get("rotate_payload_on_revoke", True))
            if remove
            else False
        )
        points = _collect_k_points(recs, k)
        if add and not rotate:
            used_x = {_decode_share(r["header"])[0] for r in recs}
            for ref in add:
                rid = _stable_recipient_id(ref)
                x_new = _x_from_recipient_id(rid, used_x)
                y_new = _lagrange_interpolate_at(x_new, points, _P)
                recs.append({"id": rid, "header": _encode_share(x_new, y_new)})
            updated = {
                "mode": _MODE,
                "payload": env["payload"],
                "recipient_alg": _RECIP_ALG,
                "recipients": recs,
                "shared": dict(env.get("shared", {})),
            }
            return updated  # type: ignore[return-value]
        _ = _lagrange_interpolate_at(0, points, _P)
        new_cek = os.urandom(cek_len)
        payload = _expect_aead_payload(env)
        pt = _aes_gcm_decrypt(
            cek=_int_to_bytes(_lagrange_interpolate_at(0, points, _P)).rjust(
                cek_len, b"\x00"
            ),
            nonce=payload["nonce"],
            ct=payload["ct"],
            tag=payload["tag"],
            aad=payload.get("aad"),
        )
        nonce, ct, tag = _aes_gcm_encrypt(new_cek, pt, payload.get("aad"))
        secret = _bytes_to_int(new_cek)
        coeffs = [secret] + [
            int.from_bytes(os.urandom(64), "big") % _P for _ in range(max(0, k - 1))
        ]
        used_x: set[int] = set()
        new_recs: List[Dict[str, Any]] = []
        base_ids = [r["id"] for r in recs]
        add_ids: List[str] = []
        add = add or []
        for ref in add:
            add_ids.append(_stable_recipient_id(ref))
        all_ids = base_ids + add_ids
        for rid in all_ids:
            x = _x_from_recipient_id(rid, used_x)
            y = _poly_eval_at(x, coeffs, _P)
            new_recs.append({"id": rid, "header": _encode_share(x, y)})
        updated_payload = {
            "kind": "aead",
            "alg": payload["alg"],
            "nonce": nonce,
            "ct": ct,
            "tag": tag,
            "aad": payload.get("aad"),
        }
        updated = {
            "mode": _MODE,
            "payload": updated_payload,
            "recipient_alg": _RECIP_ALG,
            "recipients": new_recs,
            "shared": {
                **dict(env.get("shared", {})),
                "cek_len": cek_len.to_bytes(2, "big"),
                "threshold_k": k.to_bytes(2, "big"),
            },
        }
        return updated  # type: ignore[return-value]


# ============================== local helpers ================================


def _decode_k(env: MultiRecipientEnvelope) -> int:
    s = env.get("shared", {}) or {}
    k_b = s.get("threshold_k")
    if not isinstance(k_b, (bytes, bytearray)):
        raise ValueError("Envelope missing 'shared.threshold_k'.")
    return int.from_bytes(k_b, "big")


def _decode_cek_len(env: MultiRecipientEnvelope) -> int:
    s = env.get("shared", {}) or {}
    b = s.get("cek_len")
    if not isinstance(b, (bytes, bytearray)):
        return _CEK_LEN
    return int.from_bytes(b, "big")


def _expect_aead_payload(env: MultiRecipientEnvelope) -> Dict[str, Any]:
    payload = env.get("payload")
    if not isinstance(payload, dict) or payload.get("kind") != "aead":
        raise ValueError("Envelope payload is not AEAD kind.")
    for key in ("alg", "nonce", "ct", "tag"):
        if key not in payload:
            raise ValueError(f"Envelope payload missing '{key}'.")
    if payload["alg"] != _PAYLOAD_AEAD_DEFAULT:
        raise ValueError("Unsupported payload AEAD algorithm.")
    return payload  # type: ignore[return-value]


def _find_share_for(rid: str, env: MultiRecipientEnvelope) -> Optional[bytes]:
    for r in env.get("recipients", []):
        if r.get("id") == rid:
            h = r.get("header")
            if isinstance(h, (bytes, bytearray)):
                return bytes(h)
    return None


def _collect_k_points(
    recs: Sequence[Mapping[str, Any]], k: int
) -> List[Tuple[int, int]]:
    points: List[Tuple[int, int]] = []
    seen: set[int] = set()
    for r in recs:
        h = r.get("header")
        if not isinstance(h, (bytes, bytearray)):
            continue
        x, y = _decode_share(h)
        if x in seen:
            continue
        seen.add(x)
        points.append((x, y))
        if len(points) >= k:
            break
    if len(points) < k:
        raise ValueError(
            f"Envelope has only {len(points)} usable shares; need at least {k}."
        )
    return points
